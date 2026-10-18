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

Uygulama sifre istemez. AKBAS logosuyla yaklasik 1,6 saniyelik acilis ekranindan
sonra dashboard otomatik acilir. Oturum suresi doldugunda ayni ekran oturumu
yeniden baslatir; kullanicinin sifre girmesi gerekmez.

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

Inno Setup 6 kurulu bir geliştirme bilgisayarında installer oluşturmak için:

```text
build_installer_windows.bat
```

Oluşan installer: `installer-dist\KuyumcuTakip-Setup-1.0.0.exe`

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

`build_mac.sh`, sidebar logosundan macOS `.icns` uygulama ikonunu üretir ve PyInstaller ile Python runtime'ını ve gerekli Python bağımlılıklarını `.app` paketinin içine alır. Temiz bir Mac'te ayrı Python kurulumu gerekmeden çalışması hedeflenir.

GitHub Actions workflow'u sürüm etiketi pushlandığında Apple Silicon ve Intel için ayrı `.dmg` paketleri üretir.

PyInstaller komutu macOS için `:` data ayıracını kullanır:

```bash
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

Uygulama ilk açılışta temiz ve boş bir database oluşturur. Database build veya uygulama klasörüne yazılmaz; bu nedenle uygulama güncellendiğinde mevcut kayıtlar korunur.

Farklı bir yol kullanmak istersen `DB_PATH` ortam değişkeni verilebilir.

## Yedekleme ve geri yükleme

Uygulama açıldığında günde bir kez otomatik SQLite yedeği alınır ve son 14 günlük yedekler saklanır. Migration öncesinde de ayrıca yedek alınır. Üstteki üç nokta menüsündeki `YEDEK AL` seçeneği elle yedek oluşturur. `SON YEDEĞİ GERİ YÜKLE` düğmesi restore öncesinde mevcut database'i ayrıca yedekleyip son sağlam yedeği geri yükler.

Database ve backup klasörleri:

```text
%APPDATA%\KuyumcuTakip\kuyumcu.db
%APPDATA%\KuyumcuTakip\backups\
~/Library/Application Support/KuyumcuTakip/kuyumcu.db
~/Library/Application Support/KuyumcuTakip/backups/
```

`TÜM VERİLERİ DIŞA AKTAR` düğmesi ayrıca okunabilir JSON dışa aktarımı üretir.

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


## Gram stock and expenses

Stock checks use grams only. Existing purchase/sale forms are unchanged.
Autocomplete uses one custom listbox, with no native datalist; it supports search,
scrolling, pointer selection, keyboard navigation and closing with Escape or blur.

Expenses are entered in has, to three decimal places, in the same unit as the
existing milyem profit calculation (grams * purity difference / 1000).
Total milyem profit combines normal and scrap sales. Net profit is total milyem
profit minus all recorded expenses; no price or currency conversion is used.
Only the expense form shows three compact summary cards on the right
on desktop; only small screens stack the cards below the form. The expense
history stays below the form and summary. The dashboard uses four KPI cards and compact sales/profit, stock, and account
columns with the same existing data, without an added expense summary. Expenses support edit/delete and are
included in SQLite backups and JSON exports.


The Cari page renders one table for the active All/Customers/Suppliers/Payments
filter. Net has balance is highlighted with positive, negative, and zero states.
Each account provides a read-only detail dialog with existing sales, purchases,
transaction payments, and standalone account payments, including scrap activity.
The detail view reads existing APIs without recalculating or changing balances.


Remaining inventory has is based on the unsold grams at the original purchase
purity, independently of sale purity and profit. Fully sold quantities have zero
remaining grams, has, and inventory value. Stock screens omit zero-gram entries
without removing purchase/sale history. Notes accept up to 500 characters in the API and form controls. Existing longer
notes remain stored and viewable. Table notes are truncated visually and open in
a read-only dialog. Transaction note inputs start at one line and resize up to
three; expense notes start at two and resize up to five.

Transaction forms calculate has automatically unless `has_override` is provided.
The override is stored in the existing has column without a schema migration;
list responses include its full value for lossless editing. Clearing the override
returns to automatic calculation. Gram-based stock checks and the existing
milyem profit formula remain unchanged. The recorded has continues to drive the
existing cari and transaction payment calculations. The UI truncates displayed
numbers to at most two decimal places without changing stored values or input
precision. Cari history actions open the underlying transaction or payment form.

## Mac teslim paketi

Apple Silicon ve Intel DMG dosyalarini ayni GitHub surumunden indirin; eski yerel
DMG dosyalarini guncel surum yerine kullanmayin. Her DMG, KURULUM.txt ve kaynak
commitini belirten SURUM.txt icerir. Workflow her mimaride testleri calistirir,
paketin guncel statik dosyalari icerdigini ve uygulamanin gecici, bos bir
veritabaninda acildigini kontrol eder. Paket musteri veritabani icermez.

Bu paketler Developer ID ile imzali/noter onayli degildir. Ilk acilis ve mevcut
kayitlari koruyarak guncelleme adimlari MAC_KURULUM.txt icindedir.

## Tema

Sidebar logosu acik/koyu tema dugmesidir. Tema yalnizca renkleri degistirir;
doldurulmus formu, secilen urunu ve finansal hesaplamalari degistirmez.

## Toplam stoktan satis ve mevcut veriler

Normal ve hurda satis ayni cins/ayarin toplam gram stokundan secilir.
Yeni satislar FIFO ile birden fazla alisa dagitilabilir; tek satis kaydi,
dogru gram cikisi ve agirlikli milyem kari korunur. Dagilim miktari ve maliyet
bilgisi SQLite icinde satisla birlikte tek transaction'da saklanir.

Schema 5, mevcut tablolara stoktan satis isareti ve ayri dagilim tablosu ekler.
Schema 4 kayitlari yeniden yazilmaz veya otomatik olarak FIFO'ya cevrilmez.
Guncelleme oncesi veritabani yedeklenir. Kurulum ve guvenli guncelleme icin
GUNCELLEME.txt dosyasini izleyin; Application Support klasorunu silmeyin.


## Minimal application preferences and manual has entry

The three-dot menu opens Settings. Theme uses the existing local theme preference.
Backup frequency is stored separately in `ui_settings.json` beside the database:
`daily` preserves the existing first-launch-per-day backup; `startup` adds a
verified backup at every startup. Neither option disables the existing daily
backup or changes retention. Settings show the latest valid backup timestamp and
build version when packaged. The frequency applies at the next application
startup; this is not an unattended timer while the application is running.

Typing manual has derives transaction purity as has / grams * 1000, leaving grams
and source purchase purity unchanged. Zero grams blocks manual has submission.
Editing transaction purity returns to automatic has calculation. The Automatic
button restores the purity from before the current manual entry. Existing rows
are not recalculated when opening or changing settings; old manual entries are
only synchronized when the user changes the has or gram input. Profit continues
to use the existing purity-difference formula, with the entered transaction purity.
