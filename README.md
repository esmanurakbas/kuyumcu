# AKBAŞ Kuyumcu Takip

FastAPI backend ve sade HTML/CSS/JavaScript frontend ile geliştirilmiş kuyumcu takip uygulaması.

## Yerelde çalıştırma

```bash
pip install -r requirements.txt
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Tarayıcıdan aç:

```text
http://127.0.0.1:8000
```

Giriş şifresi:

```text
2526E
```

## Windows masaüstü uygulaması

`desktop.py`, mevcut FastAPI uygulamasını arka planda boş bir local portta başlatır ve arayüzü PyWebView penceresinde açar. Kullanıcı tarayıcı veya localhost adresi görmez.

### Windows local çalıştırma

Windows'ta normal kullanım için `start.bat` dosyasına çift tıkla. Script `.venv` yoksa oluşturur, eksik paketleri kurar ve masaüstü uygulamasını açar.

```text
start.bat
```

### Windows exe oluşturma

`.exe` paketi Windows üzerinde oluşturulmalıdır. Windows için PyInstaller `;` data ayıracını kullanır.

```text
build_windows.bat
```

Oluşan dosya:

```text
dist\Kuyumcu Takip\Kuyumcu Takip.exe
```

`build_windows.bat`, PyInstaller ile Python runtime'ını ve gerekli Python bağımlılıklarını `.exe` klasörünün içine alacak şekilde hazırlandı. Temiz bir Windows bilgisayarda ayrı Python kurulumu gerekmeden çalışması hedeflenir.

## macOS masaüstü uygulaması

### macOS local çalıştırma

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python desktop.py
```

### macOS app oluşturma

`.app` paketi Mac üzerinde oluşturulmalıdır. Windows üzerinde macOS `.app` üretmeye çalışma.

```bash
source .venv/bin/activate
python -m pip install pyinstaller
chmod +x build_mac.sh
./build_mac.sh
```

Oluşan dosya:

```text
dist/Kuyumcu Takip.app
```

`build_mac.sh`, PyInstaller ile Python runtime'ını ve gerekli Python bağımlılıklarını `.app` paketinin içine alacak şekilde hazırlandı. Temiz bir Mac'te ayrı Python kurulumu gerekmeden çalışması hedeflenir.

PyInstaller komutu macOS için `:` data ayıracını kullanır:

```bash
python -m PyInstaller \
  --noconfirm \
  --clean \
  --windowed \
  --name "Kuyumcu Takip" \
  --add-data "static:static" \
  --add-data "data:data" \
  --collect-all webview \
  --collect-submodules uvicorn \
  --collect-submodules fastapi \
  --collect-submodules starlette \
  desktop.py
```

## Database konumu

Normal geliştirme modunda SQLite yolu:

```text
data/kuyumcu.db
```

Windows masaüstü uygulamasında SQLite yolu:

```text
%APPDATA%\KuyumcuTakip\kuyumcu.db
```

macOS masaüstü uygulamasında SQLite yolu:

```text
~/Library/Application Support/KuyumcuTakip/kuyumcu.db
```

Uygulama ilk açılışta bu dosya yoksa, paket içindeki `data/kuyumcu.db` varsa kullanıcı klasörüne kopyalar. Böylece `.exe` veya `.app` paketinin yazılamayan iç klasörlerine database yazmaya çalışmaz.

Farklı bir yol kullanmak istersen `DB_PATH` ortam değişkeni verilebilir.

## Yedek alma

Dashboard üzerindeki `TÜM VERİLERİ DIŞA AKTAR` butonu tüm verileri JSON olarak indirir.

Masaüstü sürümünde database dosyası ayrıca burada bulunur:

```text
%APPDATA%\KuyumcuTakip\kuyumcu.db
~/Library/Application Support/KuyumcuTakip/kuyumcu.db
```

## Deploy

Render gibi servislerde başlangıç komutu:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

Frontend API istekleri relatif `/api/...` yollarını kullanır.

## Test

```bash
python -m pytest -q
python -m py_compile main.py
node --check static/app.js
```
