#!/usr/bin/env bash
set -euo pipefail

if [[ "${OSTYPE:-}" != darwin* ]]; then
  echo "Bu script macOS uzerinde calistirilmalidir."
  exit 1
fi

if ! python -c "import PyInstaller" >/dev/null 2>&1; then
  echo "PyInstaller kurulu degil. Once su komutu calistir:"
  echo "python -m pip install pyinstaller"
  exit 1
fi

python -m PyInstaller \
  --noconfirm \
  --clean \
  --windowed \
  --name "Kuyumcu Takip" \
  --add-data "static:static" \
  --collect-all webview \
  --collect-submodules uvicorn \
  --collect-submodules fastapi \
  --collect-submodules starlette \
  desktop.py

echo "Build tamamlandi: dist/Kuyumcu Takip.app"
echo "Bu .app paketi Python runtime ve gerekli Python bagimliliklarini icine alir."
