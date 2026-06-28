# 💎 Kuyumcu Takip Sistemi - Streamlit

## Kurulum ve Çalıştırma

### 1. Bağımlılıkları Yükleyin
```bash
pip install -r requirements_streamlit.txt
```

### 2. Uygulamayı Başlatın
```bash
streamlit run streamlit_app.py
```

### 3. Tarayıcıda Açın
Uygulama otomatik olarak tarayıcıda açılacaktır (genelde http://localhost:8501)

---

## Özellikler

### ✅ Gerçekleştirilen Tüm İstekler:

1. **Soft Pastel Renk Paleti**
   - 🟢 Alış: Soft Yeşil (#C8E6C9 / #E8F5E9)
   - 🔴 Satış: Soft Kırmızı (#FFCDD2 / #FFEBEE)
   - Minimalist beyaz/gri arayüz

2. **Otomatik Has Hesaplama**
   - Has Altın alanı KİLİTLİ (kullanıcı giremez)
   - Formül: Has = Gram × Milyem × Adet / 1000
   - Ayar otomatik Milyem'e dönüştürülür

3. **Dynamic Dropdowns**
   - Cins: Dropdown (Bilezik, Çeyrek, Külçe vb.)
   - Müşteri/Tedarikçi: Kayıtlı kişiler + yeni ekleme

4. **Çift Yönlü Cari Yönetim**
   - Kişi bazlı özet (tüm cariler)
   - Seçili kişi için detaylı hareket
   - Net bakiye (Has + TL)
   - Alış/Satış renk ayrımı

5. **Kaydet/Sil Özellikleri**
   - Her formdaki "Kaydet" butonu
   - Her satırda "🗑️ Sil" butonu
   - Anlık güncelleme

6. **Arama ve Filtreleme**
   - Her sayfada search bar
   - Canlı filtreleme

7. **5 Ana Modül**
   - 🟢 Alış
   - 🔴 Satış
   - ♻️ Hurda
   - 📦 Stok
   - 💰 Cari

---

## Veritabanı

- SQLite (kuyumcu.db)
- 3 tablo: alis, satis, hurda
- Otomatik oluşturulur

---

## Notlar

- Has hesaplama tamamen otomatik
- Milyem = (Ayar / 24) × 1000
- Cari sayfası hem alış hem satışı mahsup eder
- Tüm sayılar formatlanmış (Has: 3 ondalık, TL: 2 ondalık)
