# 📊 KUYUMCU TAKİP SİSTEMİ - HESAPLAMA DENETİM RAPORU

**Tarih:** 28 Haziran 2026  
**Sistem:** Kuyumcu Stok Cari Satış Sistemi  
**Denetim Kapsamı:** Has hesaplamaları, Stok formülleri, Cari akışı, Dashboard toplamları

---

## ✅ TÜM HESAPLAMALAR DOĞRU

### 1️⃣ HAS GRAM HESAPLAMALARI

**Lokasyon:** `main.py` satır 106-107

```python
def calc_has(adet: Any, gram: Any, milyem: Any) -> Decimal:
    return q(d(adet) * d(gram) * d(milyem) / Decimal("1000"), HAS_Q)
```

**Formül:** `Has = (Adet × Gram × Milyem) / 1000`

✅ **DOĞRU** - Formül tam olarak kuyumculuk standardına uygun  
✅ **DOĞRU** - 3 ondalık yuvarlaması (HAS_Q = 0.001)  
✅ **DOĞRU** - Decimal kullanımı (float precision hatası yok)  
✅ **DOĞRU** - Tüm sayfalarda (ALIŞ, SATIŞ, HURDA) aynı formül kullanılıyor

**Boş Satır Koruması:** Python backend'de Decimal kullanımı ve `d()` fonksiyonu (satır 79-88) ile None ve boş değerler ZERO'ya çevriliyor. Excel'deki #VALUE! hatası riski YOK.

---

### 2️⃣ STOK SAYFASI HESAPLAMA DOĞRULUĞU

**Lokasyon:** `main.py` satır 361-426

#### Alış Has Toplamı
```python
for row in fetch_all(conn, "alis"):
    item = get(row["cinsi"], row["ayar"])
    item["alis_has"] += d(row["has"])
    item["kalan_has"] += d(row["has"])
```
✅ **DOĞRU** - ALIŞ tablosundan has değerleri toplanıyor

#### Satış Has Toplamı
```python
for row in fetch_all(conn, "satis"):
    item = get(row["cinsi"], row["ayar"])
    item["satis_has"] += d(row["has"])
    item["kalan_has"] -= d(row["has"])
```
✅ **DOĞRU** - SATIŞ tablosundan has değerleri çıkarılıyor

#### Hurda Has Dahil Etme (satır 395-406)
```python
for row in fetch_all(conn, "hurda"):
    item = get(row["cinsi"], row["ayar"])
    sign = Decimal("1") if row["islem_turu"] == "ALIS" else Decimal("-1")
    item["kalan_has"] += sign * d(row["has"])
    item["hurda_kalan_has"] += sign * d(row["has"])
    if sign > 0:
        item["alis_has"] += d(row["has"])
    else:
        item["satis_has"] += d(row["has"])
```
✅ **DOĞRU** - HURDA tablosundan ALIŞ (+) ve SATIŞ (-) ayrımı yapılıyor  
✅ **DOĞRU** - Hurda has ayrı kolonda takip ediliyor  
✅ **RİSK YOK** - Çift sayım yok, her işlem bir kere ekleniyor

#### Kalan Has Formülü
```
Kalan Has = Alış Has + Hurda Alış Has - Satış Has - Hurda Satış Has
```
✅ **DOĞRU** - Matematiksel olarak hatasız

#### Ortalama Has Maliyeti (satır 410)
```python
avg = item["alis_maliyet"] / item["alis_has"] if item["alis_has"] > 0 else ZERO
```
✅ **DOĞRU** - Sıfıra bölme koruması var  
✅ **DOĞRU** - Sadece alış maliyetleri kullanılıyor (satış dahil değil)

---

### 3️⃣ CARİ SAYFASI VE BORÇ/ALACAK AKIŞI

**Lokasyon:** `main.py` satır 442-484

#### Alış Carileri (Tedarikçi)
```python
for row in fetch_all(conn, "alis"):
    add(row["tedarikci"], "TEDARİKÇİ", purchase_total(row), d(row["odenen"]), row["tarih"])
```
✅ **DOĞRU** - Tedarikçiler için toplam tutar ve ödenen takip ediliyor

#### Satış Carileri (Müşteri)
```python
for row in fetch_all(conn, "satis"):
    add(row["musteri"], "MÜŞTERİ", sale_total(row), d(row["alinan"]), row["tarih"])
```
✅ **DOĞRU** - Müşteriler için toplam tutar ve tahsilat takip ediliyor

#### Hurda İşlemlerinde Cari Ayrımı (satır 467-469)
```python
for row in fetch_all(conn, "hurda"):
    tip = "TEDARİKÇİ" if row["islem_turu"] == "ALIS" else "MÜŞTERİ"
    add(row["kisi"], tip, scrap_total(row), d(row["odenen_veya_alinan"]), row["tarih"])
```
✅ **DOĞRU** - HURDA ALIŞ → TEDARİKÇİ olarak kaydediliyor  
✅ **DOĞRU** - HURDA SATIŞ → MÜŞTERİ olarak kaydediliyor  
✅ **RİSK YOK** - Hurda işlemleri doğru tarafa ekleniyor, karışma yok

#### Bakiye Hesaplama (satır 473)
```python
bakiye = cari["toplam_islem"] - cari["toplam_odeme_alma"]
```
✅ **DOĞRU** - Bakiye = İşlem Toplamı - Ödeme/Tahsilat  
✅ **DOĞRU** - Pozitif bakiye = Bize borçlu, Negatif = Biz borçlu

---

### 4️⃣ DASHBOARD ÖZET TABLOSU

**Lokasyon:** `main.py` satır 704-737

#### Toplam Alış
```python
"toplam_alis": as_float(sum((purchase_total(r) for r in alis_rows), ZERO), MONEY_Q)
```
✅ **DOĞRU** - fetch_all() tüm kayıtları çekiyor, aralık sınırı yok

#### Toplam Satış
```python
"toplam_satis": as_float(sum((sale_total(r) for r in satis_rows), ZERO), MONEY_Q)
```
✅ **DOĞRU** - Tüm satışlar dahil

#### Günlük Satış (satır 715)
```python
daily_sales = sum((sale_total(row) for row in satis_rows if row["tarih"] == today_text), ZERO)
```
✅ **DOĞRU** - Sadece bugünün kayıtları filtreleniyor

#### Toplam Kar (satır 714)
```python
total_profit = sum((sale_profit(conn, row) for row in satis_rows), ZERO)
```
✅ **DOĞRU** - Her satışın karı ayrı hesaplanıp toplanıyor

#### Stok Değeri (satır 730)
```python
"stok_degeri": as_float(sum((d(s["stok_degeri"]) for s in stocks), ZERO), MONEY_Q)
```
✅ **DOĞRU** - Stok hesaplamasından gelen değerler toplanıyor

#### Müşteri/Tedarikçi Borçları (satır 717-718)
```python
total_customer_debt = sum((d(c["bakiye"]) for c in cariler if c["tip"] == "MÜŞTERİ"), ZERO)
total_supplier_debt = sum((d(c["bakiye"]) for c in cariler if c["tip"] == "TEDARİKÇİ"), ZERO)
```
✅ **DOĞRU** - Cari tipine göre ayrılıyor

**ARALUK SORUNU:** SQL sorguları `SELECT * FROM tablo` şeklinde, yeni veri eklendiğinde otomatik dahil olur. Excel'deki `$H$5:$H$189` gibi sabit aralık riski YOK.

---

## 🆕 EKLENEN YENİ ÖZELLİKLER

### 🔍 Gelişmiş Filtreleme Sistemi

Her sayfada (ALIŞ, SATIŞ, HURDA, CARİ) şu filtreler eklendi:

1. **Tarih Aralığı Filtresi**
   - Başlangıç Tarihi
   - Bitiş Tarihi

2. **Kişi Filtresi**
   - Alış sayfasında: Tedarikçi
   - Satış sayfasında: Müşteri
   - Hurda/Cari: Kişi/İsim
   - Gerçek zamanlı arama

3. **Ürün (Cins) Filtresi**
   - Tüm ürünleri arayabilme
   - Kısmi eşleşme

4. **Ayar Filtresi**
   - Ayar bazlı filtreleme

5. **Filtreleri Temizle Butonu**
   - Tek tıkla tüm filtreleri sıfırlama

**Dosyalar:**
- `static/app.js` - Filtreleme mantığı (satır 185-225, 374-476)
- `static/styles.css` - Filtre panel stilleri (satır 338-393)

### 📊 Has Fiyatı Kolonu Eklendi

- Formlara `has_fiyati` alanı eklendi
- Tablolarda `has_fiyati` kolonu görünür hale getirildi
- Important-num styling ile vurgulandı (altın rengi)

---

## 📝 FORMÜL ÖZETİ

### Has Hesaplama
```
Has = (Adet × Gram × Milyem) / 1000
```

### Alış Toplam Tutar
```
Toplam = (Has × Has Fiyatı) + İşçilik + Ek Masraf
```

### Satış Toplam Tutar
```
Toplam = (Has × Has Fiyatı) + İşçilik + Ek Ücret - İndirim
```

### Hurda Toplam Tutar
```
Toplam = (Has × Has Fiyatı) + İşçilik
```

### Stok Kalan Has
```
Kalan = Alış Has - Satış Has + Hurda Alış - Hurda Satış
```

### Ortalama Has Maliyeti
```
Ortalama = Toplam Alış Maliyeti / Toplam Alış Has
```

### Satış Karı
```
Kar = Satış Toplamı - (Satılan Has × Ortalama Has Maliyeti)
```

### Cari Bakiye
```
Bakiye = Toplam İşlem - Toplam Ödeme/Tahsilat
(+ : Bize borçlu, - : Biz borçlu)
```

---

## ✅ SONUÇ

### TÜM HESAPLAMALAR DOĞRU ✓

- ✅ Has hesaplama formülü doğru
- ✅ Stok hesaplamaları hatasız
- ✅ Hurda alış/satış ayrımı doğru
- ✅ Cari hesapları doğru
- ✅ Dashboard toplamları doğru
- ✅ Çift sayım riski YOK
- ✅ Aralık sınırlaması sorunu YOK
- ✅ Boş değer hatası riski YOK (Decimal koruması)

### YENİ ÖZELLİKLER ✓

- ✅ Gelişmiş filtreleme sistemi eklendi
- ✅ Has Fiyatı kolonu eklendi
- ✅ Tablo stilleri iyileştirildi
- ✅ Important-num vurgulama eklendi

---

**Denetim Sonucu:** Sistemde hesaplama hatası bulunmamıştır. Tüm formüller kuyumculuk muhasebesi standartlarına uygundur.

**İmza:** Cascade AI - Hesaplama Denetim Sistemi
