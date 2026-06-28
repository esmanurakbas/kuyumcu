import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from typing import Optional

# Sayfa konfigürasyonu
st.set_page_config(
    page_title="Kuyumcu Takip Sistemi",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS ile Soft Pastel Tema
st.markdown("""
<style>
    .main {
        background-color: #FAFAFA;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1.5rem;
        border: none;
        transition: all 0.2s;
    }
    .btn-alis {
        background-color: #C8E6C9 !important;
        color: #2E7D32 !important;
    }
    .btn-alis:hover {
        background-color: #A5D6A7 !important;
    }
    .btn-satis {
        background-color: #FFCDD2 !important;
        color: #C62828 !important;
    }
    .btn-satis:hover {
        background-color: #EF9A9A !important;
    }
    .btn-delete {
        background-color: #FFEBEE !important;
        color: #C62828 !important;
        font-size: 0.85rem !important;
        padding: 0.3rem 0.8rem !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
    }
    .metric-alis {
        background-color: #E8F5E9;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2E7D32;
    }
    .metric-satis {
        background-color: #FFEBEE;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #C62828;
    }
    .metric-stok {
        background-color: #FFF8E1;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #F57F17;
    }
    h1, h2, h3 {
        color: #424242;
    }
    .dataframe {
        font-size: 0.9rem;
    }
    .has-locked {
        background-color: #F5F5F5;
        border: 1px solid #E0E0E0;
        padding: 0.5rem;
        border-radius: 4px;
        color: #757575;
        font-weight: 600;
    }
    div[data-baseweb="select"] > div {
        border-radius: 8px;
    }
    input[type="number"], input[type="text"], input[type="date"], textarea {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Veritabanı bağlantısı
def get_db():
    conn = sqlite3.connect('kuyumcu.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# Veritabanı başlatma
def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tarih DATE NOT NULL,
            tedarikci TEXT NOT NULL,
            cinsi TEXT NOT NULL,
            ayar REAL NOT NULL,
            adet INTEGER NOT NULL,
            gram REAL NOT NULL,
            milyem REAL NOT NULL,
            has REAL NOT NULL,
            iscilik REAL DEFAULT 0,
            ek_masraf REAL DEFAULT 0,
            odenen REAL DEFAULT 0,
            notlar TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS satis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tarih DATE NOT NULL,
            musteri TEXT NOT NULL,
            cinsi TEXT NOT NULL,
            ayar REAL NOT NULL,
            adet INTEGER NOT NULL,
            gram REAL NOT NULL,
            milyem REAL NOT NULL,
            has REAL NOT NULL,
            iscilik REAL DEFAULT 0,
            ek_ucret REAL DEFAULT 0,
            indirim REAL DEFAULT 0,
            alinan REAL DEFAULT 0,
            notlar TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hurda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tarih DATE NOT NULL,
            islem_turu TEXT NOT NULL,
            kisi TEXT NOT NULL,
            cinsi TEXT NOT NULL,
            ayar REAL NOT NULL,
            adet INTEGER NOT NULL,
            gram REAL NOT NULL,
            milyem REAL NOT NULL,
            has REAL NOT NULL,
            iscilik REAL DEFAULT 0,
            odenen_veya_alinan REAL DEFAULT 0,
            notlar TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

# Has hesaplama fonksiyonu
def hesapla_has(gram: float, milyem: float, adet: int = 1) -> float:
    return round((gram * milyem * adet) / 1000, 3)

# Ayar/Milyem dönüşümü
def ayar_to_milyem(ayar: float) -> float:
    return round((ayar / 24) * 1000, 1)

# Cins dropdown seçenekleri
CINS_SECENEKLERI = [
    "Bilezik", "Çeyrek Altın", "Yarım Altın", "Tam Altın", 
    "Gram Altın", "Zincir", "Kolye", "Yüzük", "Küpe",
    "Külçe", "Hurda Altın", "Diğer"
]

# Kayıtlı kişileri getir
def get_kisiler(tip: str = "all"):
    conn = get_db()
    kisiler = set()
    
    if tip in ["all", "tedarikci"]:
        df = pd.read_sql_query("SELECT DISTINCT tedarikci FROM alis", conn)
        kisiler.update(df['tedarikci'].tolist())
        
        df_hurda = pd.read_sql_query("SELECT DISTINCT kisi FROM hurda WHERE islem_turu='ALIŞ'", conn)
        kisiler.update(df_hurda['kisi'].tolist())
    
    if tip in ["all", "musteri"]:
        df = pd.read_sql_query("SELECT DISTINCT musteri FROM satis", conn)
        kisiler.update(df['musteri'].tolist())
        
        df_hurda = pd.read_sql_query("SELECT DISTINCT kisi FROM hurda WHERE islem_turu='SATIŞ'", conn)
        kisiler.update(df_hurda['kisi'].tolist())
    
    conn.close()
    return sorted(list(kisiler))

# ALIŞ sayfası
def sayfa_alis():
    st.markdown("## 🟢 Alış İşlemleri")
    
    with st.form("alis_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            tarih = st.date_input("Tarih", value=datetime.today())
            
            # Dropdown: Tedarikçi (kayıtlı + yeni)
            tedarikciler = ["[Yeni Tedarikçi]"] + get_kisiler("tedarikci")
            tedarikci_sec = st.selectbox("Tedarikçi", tedarikciler)
            
            if tedarikci_sec == "[Yeni Tedarikçi]":
                tedarikci = st.text_input("Yeni Tedarikçi Adı")
            else:
                tedarikci = tedarikci_sec
            
            cinsi = st.selectbox("Cins", CINS_SECENEKLERI)
            ayar = st.number_input("Ayar (0-24)", min_value=0.0, max_value=24.0, value=24.0, step=0.1)
        
        with col2:
            adet = st.number_input("Adet", min_value=1, value=1, step=1)
            gram = st.number_input("Brüt Gram", min_value=0.0, value=0.0, step=0.001, format="%.3f")
            milyem = ayar_to_milyem(ayar)
            st.text_input("Milyem (Otomatik)", value=f"{milyem:.1f}", disabled=True)
            
            # HAS - KİLİTLİ ALAN (Otomatik Hesaplama)
            has_hesap = hesapla_has(gram, milyem, adet)
            st.markdown(f"<div class='has-locked'>🔒 Has Altın: <strong>{has_hesap:.3f} gr</strong></div>", unsafe_allow_html=True)
        
        with col3:
            iscilik = st.number_input("İşçilik (TL)", min_value=0.0, value=0.0, step=0.01)
            ek_masraf = st.number_input("Ek Masraf (TL)", min_value=0.0, value=0.0, step=0.01)
            odenen = st.number_input("Ödenen (TL)", min_value=0.0, value=0.0, step=0.01)
            notlar = st.text_area("Notlar", height=80)
        
        submitted = st.form_submit_button("✅ Kaydet", use_container_width=True)
        
        if submitted:
            if not tedarikci or gram <= 0:
                st.error("⚠️ Tedarikçi ve Gram alanları zorunludur!")
            else:
                conn = get_db()
                conn.execute('''
                    INSERT INTO alis (tarih, tedarikci, cinsi, ayar, adet, gram, milyem, has, iscilik, ek_masraf, odenen, notlar)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (tarih, tedarikci, cinsi, ayar, adet, gram, milyem, has_hesap, iscilik, ek_masraf, odenen, notlar))
                conn.commit()
                conn.close()
                st.success(f"✅ Alış kaydedildi! Has: **{has_hesap:.3f} gr**")
                st.rerun()
    
    st.markdown("---")
    st.markdown("### 📋 Alış Kayıtları")
    
    # Arama
    arama = st.text_input("🔍 Arama (Tedarikçi, Cins, Not...)", "")
    
    conn = get_db()
    df = pd.read_sql_query("SELECT * FROM alis ORDER BY tarih DESC, id DESC", conn)
    conn.close()
    
    if not df.empty:
        if arama:
            df = df[df.apply(lambda row: arama.lower() in ' '.join(row.astype(str).values).lower(), axis=1)]
        
        # Sil butonları için
        for idx, row in df.iterrows():
            cols = st.columns([0.8, 0.8, 1, 0.6, 0.5, 0.6, 0.6, 0.7, 0.7, 0.7, 0.7, 1.2, 0.6])
            cols[0].write(row['tarih'])
            cols[1].write(row['tedarikci'])
            cols[2].write(row['cinsi'])
            cols[3].write(f"{row['ayar']:.1f}")
            cols[4].write(row['adet'])
            cols[5].write(f"{row['gram']:.3f}")
            cols[6].write(f"{row['milyem']:.1f}")
            cols[7].markdown(f"**{row['has']:.3f}**")
            cols[8].write(f"{row['iscilik']:.2f}")
            cols[9].write(f"{row['ek_masraf']:.2f}")
            cols[10].write(f"{row['odenen']:.2f}")
            cols[11].write(row['notlar'] or "-")
            
            if cols[12].button("🗑️", key=f"del_alis_{row['id']}"):
                conn = get_db()
                conn.execute("DELETE FROM alis WHERE id=?", (row['id'],))
                conn.commit()
                conn.close()
                st.success("✅ Kayıt silindi!")
                st.rerun()
    else:
        st.info("Henüz alış kaydı yok.")

# SATIŞ sayfası
def sayfa_satis():
    st.markdown("## 🔴 Satış İşlemleri")
    
    with st.form("satis_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            tarih = st.date_input("Tarih", value=datetime.today())
            
            # Dropdown: Müşteri (kayıtlı + yeni)
            musteriler = ["[Yeni Müşteri]"] + get_kisiler("musteri")
            musteri_sec = st.selectbox("Müşteri", musteriler)
            
            if musteri_sec == "[Yeni Müşteri]":
                musteri = st.text_input("Yeni Müşteri Adı")
            else:
                musteri = musteri_sec
            
            cinsi = st.selectbox("Cins", CINS_SECENEKLERI)
            ayar = st.number_input("Ayar (0-24)", min_value=0.0, max_value=24.0, value=24.0, step=0.1)
        
        with col2:
            adet = st.number_input("Adet", min_value=1, value=1, step=1)
            gram = st.number_input("Brüt Gram", min_value=0.0, value=0.0, step=0.001, format="%.3f")
            milyem = ayar_to_milyem(ayar)
            st.text_input("Milyem (Otomatik)", value=f"{milyem:.1f}", disabled=True)
            
            # HAS - KİLİTLİ ALAN (Otomatik Hesaplama)
            has_hesap = hesapla_has(gram, milyem, adet)
            st.markdown(f"<div class='has-locked'>🔒 Has Altın: <strong>{has_hesap:.3f} gr</strong></div>", unsafe_allow_html=True)
        
        with col3:
            iscilik = st.number_input("İşçilik (TL)", min_value=0.0, value=0.0, step=0.01)
            ek_ucret = st.number_input("Ek Ücret (TL)", min_value=0.0, value=0.0, step=0.01)
            indirim = st.number_input("İndirim (TL)", min_value=0.0, value=0.0, step=0.01)
            alinan = st.number_input("Alınan (TL)", min_value=0.0, value=0.0, step=0.01)
            notlar = st.text_area("Notlar", height=80)
        
        submitted = st.form_submit_button("✅ Kaydet", use_container_width=True)
        
        if submitted:
            if not musteri or gram <= 0:
                st.error("⚠️ Müşteri ve Gram alanları zorunludur!")
            else:
                conn = get_db()
                conn.execute('''
                    INSERT INTO satis (tarih, musteri, cinsi, ayar, adet, gram, milyem, has, iscilik, ek_ucret, indirim, alinan, notlar)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (tarih, musteri, cinsi, ayar, adet, gram, milyem, has_hesap, iscilik, ek_ucret, indirim, alinan, notlar))
                conn.commit()
                conn.close()
                st.success(f"✅ Satış kaydedildi! Has: **{has_hesap:.3f} gr**")
                st.rerun()
    
    st.markdown("---")
    st.markdown("### 📋 Satış Kayıtları")
    
    # Arama
    arama = st.text_input("🔍 Arama (Müşteri, Cins, Not...)", "")
    
    conn = get_db()
    df = pd.read_sql_query("SELECT * FROM satis ORDER BY tarih DESC, id DESC", conn)
    conn.close()
    
    if not df.empty:
        if arama:
            df = df[df.apply(lambda row: arama.lower() in ' '.join(row.astype(str).values).lower(), axis=1)]
        
        # Sil butonları için
        for idx, row in df.iterrows():
            cols = st.columns([0.8, 0.8, 1, 0.6, 0.5, 0.6, 0.6, 0.7, 0.7, 0.7, 0.7, 0.7, 1.2, 0.6])
            cols[0].write(row['tarih'])
            cols[1].write(row['musteri'])
            cols[2].write(row['cinsi'])
            cols[3].write(f"{row['ayar']:.1f}")
            cols[4].write(row['adet'])
            cols[5].write(f"{row['gram']:.3f}")
            cols[6].write(f"{row['milyem']:.1f}")
            cols[7].markdown(f"**{row['has']:.3f}**")
            cols[8].write(f"{row['iscilik']:.2f}")
            cols[9].write(f"{row['ek_ucret']:.2f}")
            cols[10].write(f"{row['indirim']:.2f}")
            cols[11].write(f"{row['alinan']:.2f}")
            cols[12].write(row['notlar'] or "-")
            
            if cols[13].button("🗑️", key=f"del_satis_{row['id']}"):
                conn = get_db()
                conn.execute("DELETE FROM satis WHERE id=?", (row['id'],))
                conn.commit()
                conn.close()
                st.success("✅ Kayıt silindi!")
                st.rerun()
    else:
        st.info("Henüz satış kaydı yok.")

# HURDA sayfası
def sayfa_hurda():
    st.markdown("## ♻️ Hurda İşlemleri")
    
    with st.form("hurda_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            tarih = st.date_input("Tarih", value=datetime.today())
            islem_turu = st.selectbox("İşlem Türü", ["ALIŞ", "SATIŞ"])
            
            # Dropdown: Kişi (kayıtlı + yeni)
            kisiler = ["[Yeni Kişi]"] + get_kisiler("all")
            kisi_sec = st.selectbox("Kişi", kisiler)
            
            if kisi_sec == "[Yeni Kişi]":
                kisi = st.text_input("Yeni Kişi Adı")
            else:
                kisi = kisi_sec
            
            cinsi = st.selectbox("Cins", CINS_SECENEKLERI)
            ayar = st.number_input("Ayar (0-24)", min_value=0.0, max_value=24.0, value=24.0, step=0.1)
        
        with col2:
            adet = st.number_input("Adet", min_value=1, value=1, step=1)
            gram = st.number_input("Brüt Gram", min_value=0.0, value=0.0, step=0.001, format="%.3f")
            milyem = ayar_to_milyem(ayar)
            st.text_input("Milyem (Otomatik)", value=f"{milyem:.1f}", disabled=True)
            
            # HAS - KİLİTLİ ALAN (Otomatik Hesaplama)
            has_hesap = hesapla_has(gram, milyem, adet)
            st.markdown(f"<div class='has-locked'>🔒 Has Altın: <strong>{has_hesap:.3f} gr</strong></div>", unsafe_allow_html=True)
        
        with col3:
            iscilik = st.number_input("İşçilik (TL)", min_value=0.0, value=0.0, step=0.01)
            odenen_veya_alinan = st.number_input("Ödenen / Alınan (TL)", min_value=0.0, value=0.0, step=0.01)
            notlar = st.text_area("Notlar", height=100)
        
        submitted = st.form_submit_button("✅ Kaydet", use_container_width=True)
        
        if submitted:
            if not kisi or gram <= 0:
                st.error("⚠️ Kişi ve Gram alanları zorunludur!")
            else:
                conn = get_db()
                conn.execute('''
                    INSERT INTO hurda (tarih, islem_turu, kisi, cinsi, ayar, adet, gram, milyem, has, iscilik, odenen_veya_alinan, notlar)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (tarih, islem_turu, kisi, cinsi, ayar, adet, gram, milyem, has_hesap, iscilik, odenen_veya_alinan, notlar))
                conn.commit()
                conn.close()
                st.success(f"✅ Hurda {islem_turu.lower()} kaydedildi! Has: **{has_hesap:.3f} gr**")
                st.rerun()
    
    st.markdown("---")
    st.markdown("### 📋 Hurda Kayıtları")
    
    # Arama
    arama = st.text_input("🔍 Arama (Kişi, Cins, Not...)", "")
    
    conn = get_db()
    df = pd.read_sql_query("SELECT * FROM hurda ORDER BY tarih DESC, id DESC", conn)
    conn.close()
    
    if not df.empty:
        if arama:
            df = df[df.apply(lambda row: arama.lower() in ' '.join(row.astype(str).values).lower(), axis=1)]
        
        # Sil butonları için
        for idx, row in df.iterrows():
            cols = st.columns([0.8, 0.8, 0.8, 1, 0.6, 0.5, 0.6, 0.6, 0.7, 0.7, 0.8, 1.2, 0.6])
            cols[0].write(row['tarih'])
            
            # İşlem türüne göre renk
            islem_color = "#C8E6C9" if row['islem_turu'] == "ALIŞ" else "#FFCDD2"
            islem_text_color = "#2E7D32" if row['islem_turu'] == "ALIŞ" else "#C62828"
            cols[1].markdown(f"<span style='background-color:{islem_color};color:{islem_text_color};padding:4px 8px;border-radius:4px;font-weight:600;font-size:0.85rem'>{row['islem_turu']}</span>", unsafe_allow_html=True)
            
            cols[2].write(row['kisi'])
            cols[3].write(row['cinsi'])
            cols[4].write(f"{row['ayar']:.1f}")
            cols[5].write(row['adet'])
            cols[6].write(f"{row['gram']:.3f}")
            cols[7].write(f"{row['milyem']:.1f}")
            cols[8].markdown(f"**{row['has']:.3f}**")
            cols[9].write(f"{row['iscilik']:.2f}")
            cols[10].write(f"{row['odenen_veya_alinan']:.2f}")
            cols[11].write(row['notlar'] or "-")
            
            if cols[12].button("🗑️", key=f"del_hurda_{row['id']}"):
                conn = get_db()
                conn.execute("DELETE FROM hurda WHERE id=?", (row['id'],))
                conn.commit()
                conn.close()
                st.success("✅ Kayıt silindi!")
                st.rerun()
    else:
        st.info("Henüz hurda kaydı yok.")

# STOK sayfası
def sayfa_stok():
    st.markdown("## 📦 Stok Durumu")
    
    conn = get_db()
    
    # Alış toplamları
    df_alis = pd.read_sql_query("SELECT cinsi, ayar, SUM(has) as alis_has FROM alis GROUP BY cinsi, ayar", conn)
    
    # Satış toplamları
    df_satis = pd.read_sql_query("SELECT cinsi, ayar, SUM(has) as satis_has FROM satis GROUP BY cinsi, ayar", conn)
    
    # Hurda alış
    df_hurda_alis = pd.read_sql_query("SELECT cinsi, ayar, SUM(has) as hurda_alis_has FROM hurda WHERE islem_turu='ALIŞ' GROUP BY cinsi, ayar", conn)
    
    # Hurda satış
    df_hurda_satis = pd.read_sql_query("SELECT cinsi, ayar, SUM(has) as hurda_satis_has FROM hurda WHERE islem_turu='SATIŞ' GROUP BY cinsi, ayar", conn)
    
    conn.close()
    
    # Merge
    df_stok = df_alis.merge(df_satis, on=['cinsi', 'ayar'], how='outer')
    df_stok = df_stok.merge(df_hurda_alis, on=['cinsi', 'ayar'], how='outer')
    df_stok = df_stok.merge(df_hurda_satis, on=['cinsi', 'ayar'], how='outer')
    
    df_stok = df_stok.fillna(0)
    
    # Kalan has hesapla
    df_stok['kalan_has'] = (df_stok['alis_has'] + df_stok['hurda_alis_has']) - (df_stok['satis_has'] + df_stok['hurda_satis_has'])
    
    # Sadece stok olanları göster
    df_stok = df_stok[df_stok['kalan_has'] > 0.001]
    
    if not df_stok.empty:
        # Özet metrikler
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("<div class='metric-alis'>", unsafe_allow_html=True)
            st.metric("🟢 Toplam Alış Has", f"{df_stok['alis_has'].sum():.3f} gr")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("<div class='metric-satis'>", unsafe_allow_html=True)
            st.metric("🔴 Toplam Satış Has", f"{df_stok['satis_has'].sum():.3f} gr")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col3:
            st.markdown("<div class='metric-stok'>", unsafe_allow_html=True)
            st.metric("📦 Kalan Stok Has", f"{df_stok['kalan_has'].sum():.3f} gr")
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Arama
        arama = st.text_input("🔍 Arama (Cins, Ayar...)", "")
        
        if arama:
            df_stok = df_stok[df_stok.apply(lambda row: arama.lower() in ' '.join(row.astype(str).values).lower(), axis=1)]
        
        # Tablo
        st.dataframe(
            df_stok[['cinsi', 'ayar', 'alis_has', 'satis_has', 'hurda_alis_has', 'hurda_satis_has', 'kalan_has']].style.format({
                'ayar': '{:.1f}',
                'alis_has': '{:.3f}',
                'satis_has': '{:.3f}',
                'hurda_alis_has': '{:.3f}',
                'hurda_satis_has': '{:.3f}',
                'kalan_has': '{:.3f}'
            }).background_gradient(subset=['kalan_has'], cmap='YlGn'),
            use_container_width=True,
            height=500
        )
    else:
        st.info("Stokta ürün bulunmamaktadır.")

# CARİ sayfası (Çift Yönlü)
def sayfa_cari():
    st.markdown("## 💰 Cari Hesaplar")
    
    conn = get_db()
    
    # Tüm kişileri topla
    kisiler_all = get_kisiler("all")
    
    if not kisiler_all:
        st.info("Henüz cari kaydı yok.")
        conn.close()
        return
    
    # Kişi seçimi
    secili_kisi = st.selectbox("👤 Kişi Seçin", ["[Tüm Cariler]"] + kisiler_all)
    
    st.markdown("---")
    
    if secili_kisi == "[Tüm Cariler]":
        # Tüm carilerin özeti
        st.markdown("### 📊 Tüm Cariler - Özet")
        
        cari_list = []
        
        for kisi in kisiler_all:
            # Alış toplamı (bize sattığı)
            df_alis = pd.read_sql_query("SELECT SUM(has) as has, SUM(odenen) as odenen FROM alis WHERE tedarikci=?", conn, params=(kisi,))
            df_hurda_alis = pd.read_sql_query("SELECT SUM(has) as has, SUM(odenen_veya_alinan) as odenen FROM hurda WHERE kisi=? AND islem_turu='ALIŞ'", conn, params=(kisi,))
            
            alis_has = (df_alis['has'].iloc[0] or 0) + (df_hurda_alis['has'].iloc[0] or 0)
            alis_odenen = (df_alis['odenen'].iloc[0] or 0) + (df_hurda_alis['odenen'].iloc[0] or 0)
            
            # Satış toplamı (bizden aldığı)
            df_satis = pd.read_sql_query("SELECT SUM(has) as has, SUM(alinan) as alinan FROM satis WHERE musteri=?", conn, params=(kisi,))
            df_hurda_satis = pd.read_sql_query("SELECT SUM(has) as has, SUM(odenen_veya_alinan) as alinan FROM hurda WHERE kisi=? AND islem_turu='SATIŞ'", conn, params=(kisi,))
            
            satis_has = (df_satis['has'].iloc[0] or 0) + (df_hurda_satis['has'].iloc[0] or 0)
            satis_alinan = (df_satis['alinan'].iloc[0] or 0) + (df_hurda_satis['alinan'].iloc[0] or 0)
            
            # Net bakiye (+ ise bize borçlu, - ise biz borçluyuz)
            net_has = satis_has - alis_has
            net_para = satis_alinan - alis_odenen
            
            cari_list.append({
                'Kişi': kisi,
                'Alış Has (gr)': f"{alis_has:.3f}",
                'Satış Has (gr)': f"{satis_has:.3f}",
                'Net Has (gr)': f"{net_has:.3f}",
                'Alış Ödeme (TL)': f"{alis_odenen:.2f}",
                'Satış Tahsilat (TL)': f"{satis_alinan:.2f}",
                'Net Para (TL)': f"{net_para:.2f}"
            })
        
        df_cari = pd.DataFrame(cari_list)
        st.dataframe(df_cari, use_container_width=True, height=500)
    
    else:
        # Seçili kişinin detayı
        st.markdown(f"### 👤 {secili_kisi} - Detaylı Cari")
        
        # Alış toplamı
        df_alis = pd.read_sql_query("SELECT SUM(has) as has, SUM(odenen) as odenen FROM alis WHERE tedarikci=?", conn, params=(secili_kisi,))
        df_hurda_alis = pd.read_sql_query("SELECT SUM(has) as has, SUM(odenen_veya_alinan) as odenen FROM hurda WHERE kisi=? AND islem_turu='ALIŞ'", conn, params=(secili_kisi,))
        
        alis_has = (df_alis['has'].iloc[0] or 0) + (df_hurda_alis['has'].iloc[0] or 0)
        alis_odenen = (df_alis['odenen'].iloc[0] or 0) + (df_hurda_alis['odenen'].iloc[0] or 0)
        
        # Satış toplamı
        df_satis = pd.read_sql_query("SELECT SUM(has) as has, SUM(alinan) as alinan FROM satis WHERE musteri=?", conn, params=(secili_kisi,))
        df_hurda_satis = pd.read_sql_query("SELECT SUM(has) as has, SUM(odenen_veya_alinan) as alinan FROM hurda WHERE kisi=? AND islem_turu='SATIŞ'", conn, params=(secili_kisi,))
        
        satis_has = (df_satis['has'].iloc[0] or 0) + (df_hurda_satis['has'].iloc[0] or 0)
        satis_alinan = (df_satis['alinan'].iloc[0] or 0) + (df_hurda_satis['alinan'].iloc[0] or 0)
        
        # Net bakiye
        net_has = satis_has - alis_has
        net_para = satis_alinan - alis_odenen
        
        # Metrikler
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("<div class='metric-alis'>", unsafe_allow_html=True)
            st.metric("🟢 Alış Has (Bize Sattığı)", f"{alis_has:.3f} gr")
            st.metric("💰 Ödenen", f"{alis_odenen:.2f} TL")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("<div class='metric-satis'>", unsafe_allow_html=True)
            st.metric("🔴 Satış Has (Bizden Aldığı)", f"{satis_has:.3f} gr")
            st.metric("💰 Tahsilat", f"{satis_alinan:.2f} TL")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col3:
            st.markdown("<div class='metric-stok'>", unsafe_allow_html=True)
            st.metric("📊 Net Has Bakiye", f"{net_has:.3f} gr")
            st.metric("💵 Net Para Bakiye", f"{net_para:.2f} TL")
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 📋 İşlem Geçmişi")
        
        # Alış kayıtları
        df_alis_kayit = pd.read_sql_query("SELECT tarih, 'ALIŞ' as tip, cinsi, ayar, gram, has, odenen as tutar, notlar FROM alis WHERE tedarikci=?", conn, params=(secili_kisi,))
        df_hurda_alis_kayit = pd.read_sql_query("SELECT tarih, 'ALIŞ (Hurda)' as tip, cinsi, ayar, gram, has, odenen_veya_alinan as tutar, notlar FROM hurda WHERE kisi=? AND islem_turu='ALIŞ'", conn, params=(secili_kisi,))
        
        # Satış kayıtları
        df_satis_kayit = pd.read_sql_query("SELECT tarih, 'SATIŞ' as tip, cinsi, ayar, gram, has, alinan as tutar, notlar FROM satis WHERE musteri=?", conn, params=(secili_kisi,))
        df_hurda_satis_kayit = pd.read_sql_query("SELECT tarih, 'SATIŞ (Hurda)' as tip, cinsi, ayar, gram, has, odenen_veya_alinan as tutar, notlar FROM hurda WHERE kisi=? AND islem_turu='SATIŞ'", conn, params=(secili_kisi,))
        
        # Birleştir
        df_gecmis = pd.concat([df_alis_kayit, df_hurda_alis_kayit, df_satis_kayit, df_hurda_satis_kayit])
        df_gecmis = df_gecmis.sort_values('tarih', ascending=False)
        
        if not df_gecmis.empty:
            for idx, row in df_gecmis.iterrows():
                cols = st.columns([1, 1.2, 1.5, 0.8, 0.8, 0.8, 0.8, 2])
                cols[0].write(row['tarih'])
                
                # Tip renklendirme
                if 'ALIŞ' in row['tip']:
                    cols[1].markdown(f"<span style='background-color:#C8E6C9;color:#2E7D32;padding:4px 10px;border-radius:4px;font-weight:600;font-size:0.9rem'>{row['tip']}</span>", unsafe_allow_html=True)
                else:
                    cols[1].markdown(f"<span style='background-color:#FFCDD2;color:#C62828;padding:4px 10px;border-radius:4px;font-weight:600;font-size:0.9rem'>{row['tip']}</span>", unsafe_allow_html=True)
                
                cols[2].write(row['cinsi'])
                cols[3].write(f"{row['ayar']:.1f}")
                cols[4].write(f"{row['gram']:.3f}")
                cols[5].markdown(f"**{row['has']:.3f}**")
                cols[6].write(f"{row['tutar']:.2f} TL")
                cols[7].write(row['notlar'] or "-")
        else:
            st.info("Bu kişiye ait işlem kaydı yok.")
    
    conn.close()

# Ana uygulama
def main():
    init_db()
    
    st.sidebar.title("💎 Kuyumcu Takip")
    st.sidebar.markdown("---")
    
    menu = st.sidebar.radio(
        "Menü",
        ["🟢 Alış", "🔴 Satış", "♻️ Hurda", "📦 Stok", "💰 Cari"],
        label_visibility="collapsed"
    )
    
    if menu == "🟢 Alış":
        sayfa_alis()
    elif menu == "🔴 Satış":
        sayfa_satis()
    elif menu == "♻️ Hurda":
        sayfa_hurda()
    elif menu == "📦 Stok":
        sayfa_stok()
    elif menu == "💰 Cari":
        sayfa_cari()
    
    st.sidebar.markdown("---")
    st.sidebar.caption("© 2026 Kuyumcu Takip Sistemi")

if __name__ == "__main__":
    main()
