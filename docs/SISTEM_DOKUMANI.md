# 🏆 AKBAŞ KUYUMCU TAKİP SİSTEMİ

**Versiyon:** 1.0  
**Son Güncelleme:** Haziran 2026  
**Geliştirici Notları:** Tam otomatik stok, cari ve satış takibi

---

## 📌 SİSTEM AMACI

Bu sistem, kuyumcu işletmelerinin günlük operasyonlarını takip etmek için geliştirilmiştir.

**Ana Görevler:**
1. Altın alış/satış işlemlerini kaydetmek
2. Stok durumunu **realtime** (canlı) hesaplamak
3. Müşteri ve tedarikçi borç/alacaklarını takip etmek
4. Kâr/zarar analizlerini otomatik yapmak
5. Hurda alış/satış işlemlerini yönetmek

**Önemli:** Bu sistem Excel yerine kullanılır, tüm hesaplamalar otomatiktir.

---

## 🗂️ DOSYA YAPISI VE AÇIKLAMALARI

### 📁 Ana Dizin

```
Kuyumcu/
├── main.py                    # Backend (Sunucu) - Python FastAPI
├── kuyumcu.db                 # Veritabanı - SQLite
├── requirements.txt           # Python bağımlılıkları
├── SISTEM_DOKUMANI.md         # Bu dosya
└── static/                    # Frontend (Görsel Arayüz)
    ├── index.html             # Ana sayfa HTML
    ├── app.js                 # JavaScript mantığı
    ├── styles.css             # Görsel tasarım
    ├── logo.png               # Logo dosyası
    └── favicon.png            # Tarayıcı ikonu
```

---

## 📄 DOSYALARIN DETAYLI AÇIKLAMALARI

### 1️⃣ `main.py` - Backend (Sunucu Tarafı)

**Ne İş Yapar?**
- Veritabanı ile konuşur
- Hesaplamaları yapar
- API endpoint'leri sağlar (frontend'den gelen istekleri karşılar)

**İçindekiler:**
- **Veritabanı Bağlantısı:** SQLite veritabanını yönetir
- **Tablolar:** `alis`, `satis`, `hurda` tablolarını oluşturur
- **Hesaplama Fonksiyonları:**
  - `calc_has()` → Has hesabı: `(ADET × GRAM × MİLYEM) / 1000`
  - `stock_items()` → Stok durumunu hesaplar
  - `cari_items()` → Cari hesapları hesaplar
  - `sale_profit()` → Satış kârını hesaplar
  - `dashboard()` → Dashboard özet verilerini hazırlar

**API Endpoints (Yollar):**
- `GET /api/alis` → Alış kayıtlarını listele
- `POST /api/alis` → Yeni alış kaydı ekle
- `PUT /api/alis/{id}` → Alış kaydını güncelle
- `DELETE /api/alis/{id}` → Alış kaydını sil
- (Aynı işlemler `satis` ve `hurda` için de var)
- `GET /api/stok` → Stok durumunu getir
- `GET /api/cari` → Cari hesapları getir
- `GET /api/dashboard` → Dashboard özetini getir
- `GET /api/suggestions` → Autocomplete önerileri getir

**Önemli Notlar:**
- Tüm hesaplamalar `Decimal` kullanır (para ve has için hassas)
- Türkçe karakterler `normalize_text()` ile düzeltilir
- Stok kontrolü: Satış yapmadan önce yeterli stok var mı kontrol eder

---

### 2️⃣ `kuyumcu.db` - Veritabanı

**Ne İş Yapar?**
- Tüm verileri saklar (kalıcı hafıza)
- SQLite formatında (tek dosya, kolay yedekleme)

**Tablolar:**

#### `alis` Tablosu (Alış Kayıtları)
| Kolon | Açıklama |
|-------|----------|
| `id` | Kayıt numarası (otomatik artar) |
| `tarih` | İşlem tarihi |
| `tedarikci` | Tedarikçi adı |
| `cinsi` | Ürün adı (Çeyrek Altın, Bilezik vs.) |
| `ayar` | Ayar (22, 18, 14 vs.) |
| `adet` | Adet |
| `gram` | Gram |
| `milyem` | Milyem (saflık) |
| `has` | Hesaplanan has (otomatik) |
| `has_fiyati` | Gram başı has fiyatı |
| `iscilik` | İşçilik bedeli |
| `ek_masraf` | Ek masraflar |
| `odenen` | Ödenen miktar |
| `notlar` | Notlar (max 300 karakter) |

#### `satis` Tablosu (Satış Kayıtları)
| Kolon | Açıklama |
|-------|----------|
| `id` | Kayıt numarası |
| `tarih` | İşlem tarihi |
| `musteri` | Müşteri adı |
| `cinsi` | Ürün adı |
| `ayar` | Ayar |
| `adet` | Adet |
| `gram` | Gram |
| `milyem` | Milyem |
| `has` | Hesaplanan has |
| `has_fiyati` | Gram başı has fiyatı |
| `iscilik` | İşçilik bedeli |
| `ek_ucret` | Ek ücret |
| `indirim` | İndirim |
| `alinan` | Alınan miktar |
| `notlar` | Notlar |

#### `hurda` Tablosu (Hurda İşlemleri)
| Kolon | Açıklama |
|-------|----------|
| `id` | Kayıt numarası |
| `tarih` | İşlem tarihi |
| `islem_turu` | ALIŞ veya SATIŞ |
| `kisi` | Kişi adı |
| `cinsi` | Ürün adı |
| `ayar` | Ayar |
| `adet` | Adet |
| `gram` | Gram |
| `milyem` | Milyem |
| `has` | Hesaplanan has |
| `has_fiyati` | Gram başı has fiyatı |
| `iscilik` | İşçilik |
| `odenen_veya_alinan` | Ödenen/Alınan miktar |
| `notlar` | Notlar |

---

### 3️⃣ `static/index.html` - Ana Sayfa

**Ne İş Yapar?**
- Uygulamanın görsel çatısını oluşturur
- Sidebar (yan menü) ve topbar (üst menü) içerir

**Yapısı:**
```html
<aside class="sidebar">      ← Sol menü
  <div class="brand">         ← Logo ve "AKBAŞ" başlığı
  <nav>                       ← Navigasyon butonları
    - Dashboard
    - Alış
    - Satış
    - Hurda
    - Stok
    - Cari
</nav>

<main class="app">            ← Ana içerik alanı
  <header class="topbar">     ← Üst başlık
    - Sayfa başlığı
    - Cari slider (sadece cari sayfasında)
    - Arama çubuğu
  
  <section id="content">      ← Dinamik içerik (JS ile doldurulur)
```

**Önemli Elementler:**
- `#cari-slider` → Cari filtre slider'ı (Tedarikçi/Müşteri/Tümü)
- `#search` → Arama input'u
- `#content` → Tüm içerik buraya JavaScript ile eklenir

---

### 4️⃣ `static/app.js` - JavaScript Mantığı

**Ne İş Yapar?**
- Kullanıcı etkileşimlerini yönetir
- Backend'den veri çeker, ekrana gösterir
- Form gönderir, tablolar oluşturur

**Ana Bölümler:**

#### **State Yönetimi**
```javascript
const state = {
  view: "dashboard",           // Hangi sayfa açık
  search: "",                   // Arama terimi
  cariFilter: "tedarikci",      // Cari filtresi (tedarikçi/müşteri/tümü)
  filters: { ... },             // Tarih, kişi, ürün filtreleri
  suggestions: { ... }          // Autocomplete önerileri
}
```

#### **Forms Tanımı**
Her sayfa için form alanları:
```javascript
forms = {
  alis: [["tarih", "Tarih", "date"], ...],
  satis: [...],
  hurda: [...]
}
```

#### **Columns Tanımı**
Her sayfa için tablo kolonları:
```javascript
columns = {
  alis: ["tarih", "tedarikci", "cinsi", ...],
  stok: ["cinsi", "ayar", "kalan_has", ...],
  cari: ["isim", "tip", "bakiye", ...]
}
```

#### **Önemli Fonksiyonlar**

**`render()`**
- Ana render fonksiyonu
- Hangi sayfa açıksa o sayfayı gösterir
- Dashboard, form veya tablo oluşturur

**`renderForm(type)`**
- Alış/Satış/Hurda formlarını oluşturur
- Has hesaplama önizlemesi ekler
- Kaydet butonunu en alta ekler

**`renderTable(type, rows)`**
- Tablo oluşturur
- Filtre paneli ekler
- Edit ve Delete butonları ekler

**`filtered(rows)`**
- Arama ve filtreleri uygular
- Cari slider filtresini uygular

**`showMessage(text, isError)`**
- Toast notification gösterir
- Soft mavi veya kırmızı renk

**`showConfirm(message)`**
- Modern onay dialog'u
- Silme işlemleri için

**`api(path, options)`**
- Backend ile iletişim kurar
- JSON formatında veri alır/gönderir

**`calcHasFromForm(form)`**
- Formdan has hesaplar
- `(adet × gram × milyem) / 1000`

**Has Hesaplama Önizlemesi:**
- Kullanıcı adet/gram/milyem girince otomatik hesaplanır
- Formda canlı olarak gösterilir

**Edit Özelliği:**
- Kalem ikonuna tıklayınca form doldurulur
- Güncelleme modu aktif olur
- PUT request gönderilir

---

### 5️⃣ `static/styles.css` - Görsel Tasarım

**Ne İş Yapar?**
- Tüm görsel stilleri tanımlar
- Renk paleti, yazı tipleri, düzen

**Renk Paleti:**
```css
--gold: #C29543         /* Altın rengi (ana renk) */
--green: #3F7D58        /* Yeşil (kaydet butonu) */
--red: #C53030          /* Kırmızı (sil butonu, uyarılar) */
--blue: #2563EB         /* Mavi (bilgi) */
--text: #1F2937         /* Yazı rengi */
--muted: #6B7280        /* Soluk yazı */
--line: #E5E7EB         /* Çizgi rengi */
```

**Ana Bölümler:**

**Layout (Düzen):**
- `.sidebar` → Sol menü (240px genişlik)
- `.app` → Ana içerik alanı
- `.topbar` → Üst başlık

**Forms:**
- `.entry-form` → 12 kolonlu grid sistemi
- `.form-bottom-actions` → Kaydet butonu en altta

**Tables:**
- `table` → Modern tablo tasarımı
- `td[data-col="kalan_has"]` → Kalan has vurgulama (altın rengi)

**Buttons:**
- `.delete` → Çöp kutusu ikonu
- `.edit` → Kalem ikonu
- `.confirm-btn` → Onay dialog butonları

**Notifications:**
- `.toast` → Bildirim kutusu (sağ üstte)
- `.confirm-overlay` → Onay dialog arka planı

**Responsive:**
- 1024px altında tablet görünümü
- 640px altında mobil görünümü

---

### 6️⃣ `requirements.txt` - Python Bağımlılıkları

**Ne İş Yapar?**
- Sistemin çalışması için gerekli Python kütüphanelerini listeler

**İçerik:**
```
fastapi==0.109.0        # Web framework
uvicorn==0.27.0         # ASGI sunucusu
```

**Kurulum:**
```bash
pip install -r requirements.txt
```

---

## 🔧 SİSTEM NASIL ÇALIŞIR?

### 1. Sistem Başlatma

```bash
# Terminal/Komut İstemi'nde:
cd c:\Users\esman\Desktop\Kuyumcu
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8001
```

**Ne Olur?**
1. Python `main.py` dosyasını çalıştırır
2. FastAPI sunucusu başlar
3. SQLite veritabanı açılır (yoksa oluşturulur)
4. `http://127.0.0.1:8001` adresinde dinlemeye başlar

### 2. Tarayıcıda Açma

```
http://127.0.0.1:8001
```

**Ne Olur?**
1. Tarayıcı `static/index.html` dosyasını yükler
2. `app.js` çalışmaya başlar
3. Dashboard verilerini backend'den çeker
4. Ekrana gösterir

### 3. Alış İşlemi (Örnek Akış)

**Kullanıcı:**
1. "Alış" butonuna tıklar
2. Formu doldurur: Tarih, Tedarikçi, Ürün, Ayar, Adet, Gram, Milyem
3. "Kaydet" butonuna basar

**Sistem:**
1. `app.js` → Form verilerini toplar
2. Has hesaplar: `(adet × gram × milyem) / 1000`
3. `POST /api/alis` endpoint'ine gönderir
4. `main.py` → Verileri doğrular
5. Veritabanına kaydeder
6. `app.js` → Başarı mesajı gösterir (soft mavi toast)
7. Tabloyu yeniler

### 4. Stok Hesaplama (Realtime)

**Backend:**
```python
def stock_items():
    # Her (Ürün + Ayar) için:
    ALIŞ_HAS = Tüm alışların has toplamı
    SATIŞ_HAS = Tüm satışların has toplamı
    HURDA_ALIŞ_HAS = Hurda alışların has toplamı
    HURDA_SATIŞ_HAS = Hurda satışların has toplamı
    
    KALAN_HAS = ALIŞ_HAS - SATIŞ_HAS + HURDA_ALIŞ_HAS - HURDA_SATIŞ_HAS
    
    ORTALAMA_MALIYET = Toplam Alış Tutarı / Toplam Alış Has
    STOK_DEĞERİ = KALAN_HAS × ORTALAMA_MALIYET
```

**Uyarılar:**
- `KALAN_HAS < 0` → "STOK YETERSİZ"
- `ALIŞ_HAS <= 0` → "ALIŞ YOK"

### 5. Cari Hesaplama

**Backend:**
```python
def cari_items():
    # Her kişi için (isim, tip) çifti:
    
    ALIŞ → TEDARİKÇİ:
        alis_has += has
        toplam_islem += tutar (biz borçluyuz)
    
    SATIŞ → MÜŞTERİ:
        satis_has += has
        toplam_odeme_alma += tutar (bize borçlu)
    
    HURDA ALIŞ → TEDARİKÇİ
    HURDA SATIŞ → MÜŞTERİ
    
    KALAN_HAS = alis_has - satis_has
    BAKİYE = toplam_islem - toplam_odeme_alma
```

**Bakiye Anlamı:**
- **Müşteri için:**
  - `+Bakiye` → Bize borçlu (mal verdik, para almadık)
  - `-Bakiye` → Biz borçlu (fazla para aldık)
- **Tedarikçi için:**
  - `+Bakiye` → Bize borçlu (mal aldık, para vermedik)
  - `-Bakiye` → Biz borçlu (fazla para verdik)

### 6. Satış Kârı Hesaplama

**Backend:**
```python
def sale_profit(satış_kaydı):
    SATIŞ_TUTARI = has × has_fiyati + iscilik + ek_ucret - indirim
    
    # Stoktan ortalama maliyet çek
    ORTALAMA_MALIYET = stok.ortalama_has_maliyeti
    
    KAR = SATIŞ_TUTARI - (has × ORTALAMA_MALIYET)
```

---

## 📊 SAYFA AÇIKLAMALARI

### 🏠 Dashboard
- **Kartlar:** Toplam Stok Has, Stok Değeri, Günlük Satış, Toplam Kâr
- **Stok Özeti:** İlk 10 ürün
- **Realtime:** Tüm veriler anlık hesaplanır

### 📥 Alış
- **Form:** Tedarikçiden altın alımı
- **Hesaplama:** Has otomatik hesaplanır
- **Stok:** Alış yapınca stok artar
- **Cari:** Tedarikçi cari hesabı güncellenir

### 📤 Satış
- **Form:** Müşteriye altın satışı
- **Kontrol:** Stok yeterli mi kontrol edilir
- **Hesaplama:** Kâr otomatik hesaplanır
- **Stok:** Satış yapınca stok düşer
- **Cari:** Müşteri cari hesabı güncellenir

### ♻️ Hurda
- **Form:** Hurda alış/satış
- **İşlem Türü:** ALIŞ veya SATIŞ seçilir
- **Stok:** İşlem türüne göre stok artar/azalır
- **Cari:** Kişi cari hesabı güncellenir

### 📦 Stok
- **Tablo:** (Ürün + Ayar) bazında
- **Kolonlar:** Alış Has, Satış Has, Kalan Has, Ortalama Maliyet, Stok Değeri
- **Uyarı:** Yetersiz stok kırmızı gösterilir
- **Filtre:** Ürün, Ayar
- **Vurgulama:** Kalan Has kolonu altın rengi arka plan

### 💰 Cari
- **Tablo:** Kişi bazında (aynı kişi için tedarikçi ve müşteri AYRI kayıt)
- **Slider:** Tedarikçi | Müşteri | Tümü
- **Kolonlar:** İsim, Tip, Has Bilgileri, Para Bilgileri, Bakiye
- **Filtre:** İsim

---

## 🧮 HESAPLAMA FORMÜLLERİ

### Has Hesabı
```
HAS = (ADET × GRAM × MİLYEM) / 1000
```

**Örnek:**
```
Adet: 10
Gram: 3.5
Milyem: 916

HAS = (10 × 3.5 × 916) / 1000 = 32.06 g
```

### Alış Toplam
```
TOPLAM = HAS × HAS_FİYATI + İŞÇİLİK + EK_MASRAF
```

### Satış Toplam
```
TOPLAM = HAS × HAS_FİYATI + İŞÇİLİK + EK_ÜCRET - İNDİRİM
```

### Satış Kârı
```
KAR = SATIŞ_TUTARI - (HAS × ORTALAMA_HAS_MALİYETİ)
```

### Stok Kalan Has
```
KALAN_HAS = ALIŞ_HAS - SATIŞ_HAS + HURDA_ALIŞ_HAS - HURDA_SATIŞ_HAS
```

### Cari Bakiye
```
BAKİYE = TOPLAM_İŞLEM - TOPLAM_ÖDEME_ALMA
```

---

## 🛠️ ÖNEMLİ ÖZELLİKLER

### ✅ Türkçe Karakter Desteği
- Tüm hesaplamalar Türkçe karakterlerle çalışır
- `normalize_text()` fonksiyonu:
  - "Çeyrek Altın" ve "ceyrek altın" aynı kabul edilir
  - Büyük/küçük harf farkı yok
  - İ, ı, ş, ğ, ü, ö, ç karakterleri sorunsuz

### ✅ Autocomplete (Otomatik Tamamlama)
- Tedarikçi, Müşteri, Ürün alanlarında
- Daha önce girilen isimler önerilir
- Yazarken filtreler

### ✅ Filtreleme
- **Alış/Satış/Hurda:** Tarih, Kişi, Ürün, Ayar
- **Cari:** İsim
- **Stok:** Ürün, Ayar
- Temizle butonu ile tüm filtreler sıfırlanır

### ✅ Arama
- Tüm sayfalarda genel arama
- Tüm kolonlarda arar

### ✅ Edit (Düzenleme)
- Kalem ikonuna tıklayınca kayıt düzenlenebilir
- Form otomatik doldurulur
- "Güncelle" butonu görünür
- Stok ve cari otomatik güncellenir

### ✅ Delete (Silme)
- Çöp kutusu ikonuna tıklayınca modern onay dialog'u
- Onaylanınca kayıt silinir
- Stok ve cari otomatik güncellenir

### ✅ Toast Notifications
- Soft mavi renk (bilgi)
- Kırmızı renk (hata)
- Sağ üstten slide-in animasyonu
- 3.5 saniye sonra kaybolur

### ✅ Responsive Tasarım
- Masaüstü, tablet, mobil uyumlu
- Yan menü küçük ekranlarda tepede gösterilir

---

## 🚨 HATA KONTROL MEKANİZMALARI

### Satış Kontrolleri
1. **Stok Kontrolü:**
   ```python
   if kalan_has < satış_has:
       raise Error("STOK YETERSİZ")
   ```

2. **Alış Kontrolü:**
   ```python
   if alis_has <= 0:
       raise Error("ALIŞ YOK")
   ```

### Veri Doğrulama
- Boş alan kontrolü (required fields)
- Sayısal alanlar (adet, gram, milyem) sıfırdan büyük olmalı
- Tarih formatı kontrol edilir

### Türkçe Karakter Normalizasyonu
```python
def normalize_text(text):
    # Küçük harfe çevir
    # İ → i, ş → s, ğ → g, ü → u, ö → o, ç → c
    # Aksanları kaldır
```

### Decimal Hassasiyet
- Para ve has hesaplamalarında `Decimal` kullanılır
- Float hataları önlenir
- `0.01` hassasiyetle yuvarlanır

---

## 💾 VERİTABANI YEDEKLEMESİ

**Otomatik Yedekleme:**
- `kuyumcu.db` dosyasını kopyala
- İsim: `kuyumcu_backup_TARIH.db`
- Haftalık/aylık yedekleme önerilir

**Manuel Yedekleme:**
```bash
# Windows
copy kuyumcu.db kuyumcu_backup.db

# Linux/Mac
cp kuyumcu.db kuyumcu_backup.db
```

**Geri Yükleme:**
```bash
# Eski dosyayı sil
del kuyumcu.db  (Windows)
rm kuyumcu.db   (Linux/Mac)

# Backup'tan geri yükle
copy kuyumcu_backup.db kuyumcu.db  (Windows)
cp kuyumcu_backup.db kuyumcu.db    (Linux/Mac)
```

---

## 🔐 GÜVENLİK NOTLARI

1. **Local Kullanım:**
   - Sistem sadece `127.0.0.1` (localhost) üzerinde çalışır
   - İnternet üzerinden erişilemez
   - Güvenli

2. **Online Yapma (İsteğe Bağlı):**
   - Şifre sistemi eklenebilir
   - HTTPS kullanılmalı
   - Veritabanı şifrelenebilir

3. **Veri Güvenliği:**
   - Düzenli yedekleme yapın
   - `kuyumcu.db` dosyasını güvenli tutun
   - Cloud'a yedekleyin (Google Drive, Dropbox vs.)

---

## 📱 KULLANIM SENARYOLARI

### Senaryo 1: Yeni Alış
1. "Alış" sayfasını aç
2. Tarih seç (otomatik bugün gelir)
3. Tedarikçi adı yaz (autocomplete önerir)
4. Ürün adı yaz (Çeyrek Altın, Bilezik vs.)
5. Ayar gir (22, 18, 14)
6. Adet, Gram, Milyem gir
7. Has otomatik hesaplanır (önizleme)
8. Has Fiyatı, İşçilik, Ek Masraf gir
9. "Kaydet" butonuna bas
10. Soft mavi bildirim: "Alış kaydedildi"
11. Stok ve Cari otomatik güncellenir

### Senaryo 2: Satış Yapma
1. "Satış" sayfasını aç
2. Müşteri adı yaz
3. Ürün seç (stokta olan)
4. Adet, Gram, Milyem gir
5. Sistem stok kontrolü yapar
   - Yeterli varsa → Kaydet
   - Yoksa → "STOK YETERSİZ" hatası
6. Kâr otomatik hesaplanır
7. Cari güncellenir

### Senaryo 3: Cari Takibi
1. "Cari" sayfasını aç
2. Slider'da "Tedarikçi" seç → Sadece tedarikçiler
3. Slider'da "Müşteri" seç → Sadece müşteriler
4. İsim filtresinde ara
5. Bakiye kolonuna bak:
   - Kırmızı (+) → Bize borçlu
   - Mavi (-) → Biz borçlu

### Senaryo 4: Stok Kontrolü
1. "Stok" sayfasını aç
2. Tüm ürünlerin kalan has'ını gör
3. Kalan Has vurgulu (altın rengi)
4. Uyarı varsa kırmızı pill görünür
5. Filtre ile spesifik ürün ara

---

## 🎨 TASARIM FELSEFESİ

**Minimal ve Profesyonel:**
- Gereksiz süsleme yok
- Temiz, düzenli görünüm
- Altın rengi vurgu (kuyumcu teması)

**Kullanıcı Dostu:**
- Büyük, rahat tıklanabilir butonlar
- Açık renkler, net yazılar
- Toast notification (rahatsız etmeyen)
- Modern onay dialog'ları

**Responsive:**
- Masaüstü, tablet, mobil uyumlu
- Otomatik düzen ayarlaması

---

## 🐛 SORUN GİDERME

### Sunucu Başlamıyor
```
ERROR: Address already in use
```
**Çözüm:** Port değiştir
```bash
python -m uvicorn main:app --reload --port 8002
```

### Veritabanı Hatası
```
ERROR: Database is locked
```
**Çözüm:** 
- Sunucuyu kapat
- `kuyumcu.db-journal` dosyasını sil
- Tekrar başlat

### Has Hesaplanamıyor
- Adet, Gram, Milyem boş olmasın
- Sayı formatı doğru mu kontrol et (virgül yerine nokta)

### Türkçe Karakter Sorunu
- Backend `normalize_text()` fonksiyonu otomatik düzeltir
- Sorun devam ederse veritabanını yedekle, `kuyumcu.db` dosyasını sil, yeniden oluştur

---

## 📞 DESTEK VE GELİŞTİRME

**Yeni Özellik Önerileri:**
- Raporlama (PDF/Excel export)
- Grafik ve dashboard widget'ları
- SMS/Email bildirimleri
- Fatura/fiş yazdırma
- Çoklu kullanıcı desteği
- Şifre koruması

**Geliştirme Notları:**
- Backend: Python FastAPI
- Frontend: Vanilla JavaScript (framework yok)
- Database: SQLite
- Stil: Modern CSS (Tailwind değil, custom)

---

## 📚 KAYNAKLAR

- **FastAPI Dökümantasyonu:** https://fastapi.tiangolo.com/
- **SQLite Dökümantasyonu:** https://www.sqlite.org/docs.html
- **JavaScript MDN:** https://developer.mozilla.org/en-US/docs/Web/JavaScript

---

## ✅ KONTROL LİSTESİ

Sistem doğru çalışıyor mu? Şunları kontrol et:

- [ ] Sunucu başlıyor (`http://127.0.0.1:8001` açılıyor)
- [ ] Dashboard kartları görünüyor
- [ ] Alış formu çalışıyor, kayıt oluşturuluyor
- [ ] Satış formu çalışıyor, stok kontrolü yapıyor
- [ ] Hurda formu çalışıyor
- [ ] Stok sayfası doğru hesaplıyor
- [ ] Cari sayfası doğru hesaplıyor
- [ ] Slider (Tedarikçi/Müşteri/Tümü) çalışıyor
- [ ] Filtreler çalışıyor
- [ ] Arama çalışıyor
- [ ] Edit (kalem ikonu) çalışıyor
- [ ] Delete (çöp kutusu ikonu) çalışıyor, onay dialog'u çıkıyor
- [ ] Toast notification'lar görünüyor (soft mavi)
- [ ] Türkçe karakterler sorunsuz çalışıyor
- [ ] Kalan Has vurgulu görünüyor

---

## 🎓 SONUÇ

Bu sistem, kuyumcu işletmelerinin günlük operasyonlarını kolaylaştırmak, manuel hesaplamalardan kurtarmak ve hataları önlemek için tasarlanmıştır.

**Temel Prensipler:**
1. **Otomatik Hesaplama:** Hiçbir şeyi manuel hesaplamaya gerek yok
2. **Realtime Güncellemeler:** Her işlem anında stok ve cariyi günceller
3. **Hata Kontrolü:** Yanlış işlem yapmanızı engeller
4. **Kolay Kullanım:** Minimal, sade arayüz

**Başarılar! 🏆**
