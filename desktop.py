from __future__ import annotations

import contextlib
import os
import shutil
import socket
import sys
import threading
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path

APP_NAME = "Kuyumcu Takip"
HOST = "127.0.0.1"
STARTUP_TIMEOUT_SECONDS = 20


def resource_path(relative_path: str) -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / relative_path


def desktop_data_dir() -> Path:
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "KuyumcuTakip"
    if os.name == "nt":
        return Path(os.getenv("APPDATA", Path.home())) / "KuyumcuTakip"
    return Path(os.getenv("XDG_DATA_HOME", Path.home() / ".local" / "share")) / "KuyumcuTakip"


def prepare_database_path() -> None:
    data_dir = desktop_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)
    db_path = data_dir / "kuyumcu.db"
    os.environ.setdefault("DB_PATH", str(db_path))

    bundled_seed = resource_path("data") / "kuyumcu.db"
    if not db_path.exists() and bundled_seed.exists():
        shutil.copy2(bundled_seed, db_path)


prepare_database_path()

import uvicorn  # noqa: E402
import webview  # noqa: E402

import main as backend  # noqa: E402


@dataclass
class DesktopServer:
    server: uvicorn.Server
    thread: threading.Thread
    url: str


def find_free_port() -> int:
    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.bind((HOST, 0))
        return int(sock.getsockname()[1])


def wait_until_ready(url: str, timeout_seconds: int = STARTUP_TIMEOUT_SECONDS) -> None:
    deadline = time.time() + timeout_seconds
    last_error: Exception | None = None
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1.0) as response:
                if response.status < 500:
                    return
        except Exception as exc:  # noqa: BLE001 - startup probe should keep retrying.
            last_error = exc
        time.sleep(0.2)
    raise RuntimeError(f"Uygulama baslatilamadi: {last_error}")


def start_backend() -> DesktopServer:
    port = find_free_port()
    url = f"http://{HOST}:{port}"
    config = uvicorn.Config(
        backend.app,
        host=HOST,
        port=port,
        log_level="warning",
        access_log=False,
        lifespan="on",
    )
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, name="kuyumcu-backend", daemon=True)
    thread.start()
    wait_until_ready(f"{url}/login")
    return DesktopServer(server=server, thread=thread, url=url)


def run() -> None:
    desktop_server = start_backend()
    window = webview.create_window(
        APP_NAME,
        desktop_server.url,
        width=1280,
        height=820,
        min_size=(1040, 700),
        confirm_close=True,
    )

    def stop_backend() -> None:
        desktop_server.server.should_exit = True

    window.events.closed += stop_backend
    webview.start(debug=False)


if __name__ == "__main__":
    run()
