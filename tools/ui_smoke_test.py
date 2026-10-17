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
            cdp.wait_for("document.querySelector('.logo') !== null")
            assert cdp.evaluate("document.querySelector('input[type=password]') === null")
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

            cdp.evaluate("document.querySelector('[data-view=giderler]').click()")
            cdp.wait_for("document.querySelector('input[name=tutar]') !== null")
            cdp.evaluate("(()=>{const f=document.querySelector('.entry-form');f.elements.tutar.value='0,125';f.elements.kategori.value='Yemek';f.elements.notlar.value='UI test';f.requestSubmit()})()")
            cdp.wait_for("document.querySelector('tbody')?.innerText.includes('UI test')")
            cdp.evaluate("document.querySelector('button.icon-edit').click()")
            cdp.wait_for("document.querySelector('input[name=tutar]')?.value === '0.125'")
            cdp.evaluate("(()=>{const f=document.querySelector('.entry-form');f.elements.tutar.value='0,350';f.requestSubmit()})()")
            cdp.wait_for("document.querySelector('tbody')?.innerText.includes('0,35')")
            cdp.evaluate("document.querySelector('[data-view=alis]').click()")
            cdp.wait_for("document.querySelector('input[name=gram]') !== null")
            assert cdp.evaluate("['has_fiyati','iscilik','ek_masraf','ek_ucret','indirim'].every(name=>!document.querySelector(`.entry-form [name=${name}]`))")
            cdp.evaluate("(()=>{const i=document.querySelector('[name=cinsi]'); i.value=''; i.focus();})()")
            cdp.wait_for("document.querySelector('[name=cinsi]').getAttribute('aria-expanded') === 'true'")
            assert cdp.evaluate("!document.querySelector('[name=cinsi]').hasAttribute('list')")
            assert cdp.evaluate("document.querySelectorAll('.suggest-box:not(.hidden)').length === 1")
            assert cdp.evaluate("document.querySelector('[name=cinsi]').parentElement.querySelectorAll('.suggest-box').length === 1")
            assert cdp.evaluate("document.querySelector('.suggest-box:not(.hidden)').children.length === new Set(state.suggestions.products.map(normalize)).size")
            cdp.evaluate("(()=>{const i=document.querySelector('[name=cinsi]');i.value='BILE';i.dispatchEvent(new Event('input',{bubbles:true}));})()")
            assert cdp.evaluate("document.querySelector('.suggest-box:not(.hidden)').children.length === 1")
            cdp.evaluate("document.querySelector('.suggest-box:not(.hidden) button').click()")
            assert cdp.evaluate("document.querySelector('[name=cinsi]').value.length > 0 && document.querySelectorAll('.suggest-box:not(.hidden)').length === 0")
            cdp.evaluate("(()=>{const i=document.querySelector('[name=cinsi]');i.value='';i.dispatchEvent(new Event('input',{bubbles:true}));i.dispatchEvent(new KeyboardEvent('keydown',{key:'ArrowDown',bubbles:true}));i.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',bubbles:true}));})()")
            assert cdp.evaluate("document.querySelectorAll('.suggest-box:not(.hidden)').length === 0")
            cdp.evaluate("(()=>{const i=document.querySelector('[name=cinsi]');i.value='';i.dispatchEvent(new Event('input',{bubbles:true}));i.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}));})()")
            assert cdp.evaluate("document.querySelectorAll('.suggest-box:not(.hidden)').length === 0")
            cdp.evaluate("document.querySelector('[data-view=satis]').click()")
            cdp.wait_for("document.querySelector('input[name=satis_milyem]') !== null")
            assert cdp.evaluate("['has_fiyati','iscilik','ek_masraf','ek_ucret','indirim'].every(name=>!document.querySelector(`.entry-form [name=${name}]`))")
            cdp.evaluate("document.querySelector('[data-view=hurda_alis]').click()")
            cdp.wait_for("document.querySelector('[name=islem_turu]') !== null")
            assert cdp.evaluate("['has_fiyati','iscilik','ek_masraf','ek_ucret','indirim'].every(name=>!document.querySelector(`.entry-form [name=${name}]`))")

            cdp.evaluate("document.querySelector('[data-view=dashboard]').click()")
            cdp.wait_for("document.querySelector('#pageTitle')?.innerText === 'Dashboard'")
            cdp.wait_for("document.querySelector('.dashboard-root') !== null")
            dashboard = cdp.evaluate("fetch('/api/dashboard').then(r=>r.json()).then(r=>r.data)", await_promise=True)
            assert dashboard["toplam_gider"] == 0.350
            assert dashboard["net_kar"] == -0.350
            cards = cdp.evaluate("[...document.querySelectorAll('.expense-profit-summary')].find(p=>p.textContent.includes('Toplam Gider'))?.textContent")
            assert cards and "0,35" in cards, cards
            assert "Toplam Milyem K\u00e2r\u0131" in cards, cards
            assert "Kalan Net K\u00e2r" in cards, cards
            assert "Net K\u00e2r" in cards, cards
            baseline = json.loads((ROOT / "tools" / "original_ui.json").read_text(encoding="utf-8"))
            actual_forms = cdp.evaluate("forms")
            actual_columns = cdp.evaluate("columns")
            for name, fields in baseline["forms"].items():
                assert actual_forms[name] == fields, (name, actual_forms[name])
            for name, fields in baseline["columns"].items():
                assert actual_columns[name] == fields, (name, actual_columns[name])
            expected_nav = list(baseline["views"]) + ["giderler"]
            for view in expected_nav:
                cdp.evaluate(f"document.querySelector('[data-view={view}]').click()")
                cdp.wait_for("document.querySelector('#content').children.length > 0")
                cdp.wait_for(f"document.querySelector('#pageTitle').textContent === views[{json.dumps(view)}].title")
                body = cdp.evaluate("document.querySelector('#content').textContent")
                assert "(TL)" not in body and "TL /" not in body and "\u20ba" not in body, (view, body)
                assert "Parasal rapor" not in body, view
                if view in {"alis", "satis", "hurda_alis", "hurda_satis"}:
                    assert cdp.evaluate("['has_fiyati','iscilik','ek_masraf','ek_ucret','indirim'].every(name=>!document.querySelector(`.entry-form [name=${name}]`))"), view
                print(f"Page checked: {view}")
            cdp.call("Emulation.setDeviceMetricsOverride", {"width": 1440, "height": 1000, "deviceScaleFactor": 1, "mobile": False})
            cdp.wait_for("document.querySelector('.expenses-layout').getBoundingClientRect().width > 900")
            assert cdp.evaluate("(()=>{const a=document.querySelector('.expenses-main').getBoundingClientRect();const b=document.querySelector('.expenses-layout>.expense-profit-summary').getBoundingClientRect();return b.left>=a.right;})()")
            assert cdp.evaluate("Math.abs(document.querySelector('.expenses-main').getBoundingClientRect().top-document.querySelector('.expenses-layout>.expense-profit-summary').getBoundingClientRect().top)<2")
            assert cdp.evaluate("document.querySelector('.expenses-main').getBoundingClientRect().width < 740"), "Expense form must leave space for compact summary"
            cdp.call("Emulation.setDeviceMetricsOverride", {"width": 1024, "height": 900, "deviceScaleFactor": 1, "mobile": False})
            cdp.wait_for("document.querySelector('.expenses-layout>.expense-profit-summary').getBoundingClientRect().left >= document.querySelector('.expenses-main').getBoundingClientRect().right")
            cdp.call("Emulation.setDeviceMetricsOverride", {"width": 1440, "height": 1000, "deviceScaleFactor": 1, "mobile": False})
            cdp.evaluate("document.querySelectorAll('.toast').forEach(toast => toast.remove())")
            if os.getenv("UI_SCREENSHOT_PATH"):
                import base64
                screenshot = cdp.call("Page.captureScreenshot", {"format": "png", "captureBeyondViewport": True})
                Path(os.environ["UI_SCREENSHOT_PATH"]).write_bytes(base64.b64decode(screenshot["data"]))
            cdp.call("Emulation.setDeviceMetricsOverride", {"width": 390, "height": 844, "deviceScaleFactor": 1, "mobile": False})
            cdp.wait_for("document.querySelector('.expenses-layout>.expense-profit-summary').getBoundingClientRect().bottom <= document.querySelector('.expenses-main').getBoundingClientRect().top")
            assert cdp.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), "Expense page overflows mobile width"
            cdp.evaluate("document.querySelector('[data-view=dashboard]').click()")
            cdp.wait_for("document.querySelector('.dashboard-root')?.firstElementChild.classList.contains('expense-profit-summary')")
            print("UI smoke test passed: passwordless entry, all pages, original forms and columns, no added currency labels, expense create/edit, dashboard totals")
        finally:
            browser.terminate()
            server.should_exit = True
            thread.join(timeout=5)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python tools/ui_smoke_test.py <chrome-path>")
    run(Path(sys.argv[1]))
