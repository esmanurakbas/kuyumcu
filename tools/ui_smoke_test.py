from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
from pathlib import Path

import uvicorn
from websockets.sync.client import connect

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import main  # noqa: E402


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def wait_json(url: str, timeout: float = 20) -> object:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                return json.load(response)
        except Exception:
            time.sleep(0.2)
    raise RuntimeError(f"Timeout: {url}")


class Cdp:
    def __init__(self, url: str):
        self.ws = connect(url, origin="http://localhost")
        self.next_id = 0

    def call(self, method: str, params: dict | None = None) -> dict:
        self.next_id += 1
        call_id = self.next_id
        self.ws.send(json.dumps({"id": call_id, "method": method, "params": params or {}}))
        while True:
            message = json.loads(self.ws.recv())
            if message.get("id") == call_id:
                if "error" in message:
                    raise RuntimeError(message["error"])
                return message["result"]

    def evaluate(self, expression: str, await_promise: bool = False):
        result = self.call("Runtime.evaluate", {
            "expression": expression,
            "awaitPromise": await_promise,
            "returnByValue": True,
        })
        if "exceptionDetails" in result:
            raise RuntimeError(result["exceptionDetails"])
        return result["result"].get("value")

    def wait_for(self, expression: str, timeout: float = 15):
        deadline = time.time() + timeout
        while time.time() < deadline:
            if self.evaluate(expression):
                return
            time.sleep(0.2)
        raise AssertionError(f"UI condition failed: {expression}")


def run(chrome: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="kuyumcu-ui-") as temp:
        main.DB_PATH = Path(temp) / "data" / "kuyumcu.db"
        main.sessions.clear()
        main.login_attempts.clear()
        app_port = free_port()
        debug_port = free_port()
        server = uvicorn.Server(uvicorn.Config(main.app, host="127.0.0.1", port=app_port, log_level="error"))
        thread = threading.Thread(target=server.run, daemon=True)
        thread.start()
        wait_json(f"http://127.0.0.1:{app_port}/api/session")

        profile = Path(temp) / "chrome"
        browser = subprocess.Popen([
            str(chrome), "--headless=new", "--disable-gpu", "--no-first-run",
            "--remote-allow-origins=*", f"--remote-debugging-port={debug_port}",
            f"--user-data-dir={profile}", f"http://127.0.0.1:{app_port}/login",
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            pages = wait_json(f"http://127.0.0.1:{debug_port}/json")
            page = next(item for item in pages if item["type"] == "page")
            cdp = Cdp(page["webSocketDebuggerUrl"])
            cdp.wait_for("document.querySelector('#loginForm') !== null")
            cdp.evaluate("document.querySelector('#password').value='2526E'; document.querySelector('#loginForm').requestSubmit()")
            cdp.wait_for("location.pathname === '/' && document.querySelector('[data-view=alis]') !== null")

            payload = json.dumps({
                "tarih": "2026-10-03", "tedarikci": "ARANACAK TEDARIKCI",
                "cinsi": "BILEZIK", "ayar": "22", "adet": 1, "gram": 10,
                "milyem": 916, "has_fiyati": 3000,
            })
            result = cdp.evaluate(
                f"fetch('/api/alis',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:{json.dumps(payload)}}}).then(r=>r.json())",
                await_promise=True,
            )
            assert result["status"] == "ok", result

            cdp.evaluate("document.querySelector('[data-view=alis]').click()")
            cdp.wait_for("document.querySelector('tbody tr') !== null")
            cdp.evaluate("(()=>{const s=document.querySelector('#search');s.value='aranacak';s.dispatchEvent(new Event('input',{bubbles:true}))})()")
            cdp.wait_for("document.querySelectorAll('tbody tr').length === 1 && document.body.innerText.includes('ARANACAK TEDARIKCI')")
            cdp.evaluate("(()=>{const s=document.querySelector('#search');s.value='bulunmayan';s.dispatchEvent(new Event('input',{bubbles:true}))})()")
            cdp.wait_for("document.querySelector('.empty')?.innerText.includes('Kayıt yok')")

            cdp.evaluate("document.querySelector('[data-view=stok]').click()")
            cdp.wait_for("[...document.querySelectorAll('.page-tab')].some(b=>b.innerText==='HURDA STOK')")
            cdp.evaluate("[...document.querySelectorAll('.page-tab')].find(b=>b.innerText==='HURDA STOK').click()")
            cdp.wait_for("[...document.querySelectorAll('.page-tab.active')].some(b=>b.innerText==='HURDA STOK')")

            cdp.evaluate("document.querySelector('[data-view=cari]').click()")
            cdp.wait_for("[...document.querySelectorAll('.page-tab')].some(b=>b.innerText==='MÜŞTERİLER')")
            cdp.evaluate("[...document.querySelectorAll('.page-tab')].find(b=>b.innerText==='MÜŞTERİLER').click()")
            cdp.wait_for("[...document.querySelectorAll('.page-tab.active')].some(b=>b.innerText==='MÜŞTERİLER')")

            cdp.evaluate("document.querySelector('[data-view=dashboard]').click()")
            cdp.wait_for("document.querySelector('#pageTitle')?.innerText === 'Dashboard'")
            cdp.wait_for("document.querySelector('.dashboard-root') !== null")
            print("UI smoke test passed: login, dashboard, search, stock filter, customer filter")
        finally:
            browser.terminate()
            server.should_exit = True
            thread.join(timeout=5)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python tools/ui_smoke_test.py <chrome-path>")
    run(Path(sys.argv[1]))
