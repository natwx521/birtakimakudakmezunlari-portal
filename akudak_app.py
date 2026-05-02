import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
from datetime import datetime

# 1. SAYFA VE TEMA AYARLARI
st.set_page_config(page_title="AKÜDAK Mezunları Portalı", layout="wide")

# 2. BAĞLANTI AYARLARI
JSON_KEY_DOSYASI = 'refined-helix-495108-d4-5b0da9922a2a.json'
SPREADSHEET_ADI = 'faaliyet_kayitlari'

def baglan(worksheet_index=0):
    try:
        creds = service_account.Credentials.from_service_account_file(
            JSON_KEY_DOSYASI, 
            scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        )
        client = gspread.authorize(creds)
        return client.open(SPREADSHEET_ADI).get_worksheet(worksheet_index)
    except Exception as e:
        st.error(f"Bağlantı kurulurken hata oluştu: {e}")
        return None

# 3. VERİLERİ ÇEKME VE SAYFAYI HAZIRLAMA
sheet = baglan(0)
if sheet:
    try:
        df = pd.DataFrame(sheet.get_all_records())
    except:
        df = pd.DataFrame()
else:
    df = pd.DataFrame()

# 4. YAN MENÜ (SIDEBAR)
st.sidebar.image("resim01.png", use_container_width=True)
st.sidebar.title("🧭 AKÜDAK Menü")
sekme = st.sidebar.radio("Gitmek İstediğiniz Bölüm:", ["Ana Sayfa & Kayıt", "👤 Tırmanıcı Analizi", "🛠 Malzeme Karnesi"])

# SABİT LİSTELER
kullanicilar = ["Umut ŞEN", "Vedat AYDIN", "Mehmet AKŞİPAL", "Tanju DEMİREL", "Yavuz S. ÇAMUR","Erhan YALÇIN", "Emre DOĞAN", "Misafir"]
stiller = ["Lider-Spor", "Lider-Geleneksel", "Top-Rope"]
zorluk_dereceleri = ["IV", "V-", "V", "V+", "VI-", "VI", "VI+", "VII-", "VII", "VII+", "VIII-", "VIII", "VIII+", "IX-", "IX"]
malzemeler = ["Petzl Volta Guide 9.0mm (80m)", "Corax LT Kemer M", "Corax LT Kemer XL", "Petzl Reverso Kırm.", "Petzl Reverso Yeşil.", "Ekspres Set"]

# --- SEKMELER ---

if sekme == "Ana Sayfa & Kayıt":
    st.title("🚀 BİR TAKIM AKÜDAK MEZUNLARI VERİ GİRİŞİ")
    
    # 🪢 ANA İP DURUM PANELİ
    ip_ismi = "Petzl Volta Guide 9.0mm (80m)"
    if not df.empty and ip_ismi in df['Malzeme'].values:
        ip_df = df[df['Malzeme'] == ip_ismi]
        toplam_metraj = ip_df['Toplam_Ip'].sum()
        toplam_dusus = ip_df['Dusus'].sum()
        
        st.subheader(f"🪢 1 No'lu İp Durumu ({ip_ismi})")
        c1, c2, c3 = st.columns(3)
        c1.metric("Toplam Kullanım", f"{toplam_metraj} m")
        c2.metric("Sert Düşüş", f"{toplam_dusus} Adet")
        
        is_safe = "GÜVENLİ ✅" if toplam_dusus < 5 and toplam_metraj < 5000 else "RİSKLİ / KONTROL ET ⚠️"
        c3.info(f"Emniyet Durumu: {is_safe}")
    
    st.divider()
    
    # 📝 KAYIT FORMU
    with st.form("yeni_kayit_formu", clear_on_submit=True):
        st.subheader("📝 Yeni Faaliyet Girişi")
        col_a, col_b = st.columns(2)
        
        with col_a:
            kisi = st.selectbox("Tırmanıcı", kullanicilar)
            tarih = st.date_input("Tarih", datetime.now())
            sektor = st.text_input("Sektör (Örn: Geyikbayırı)")
            rota = st.text_input("Rota Adı")
            
        with col_b:
            stil = st.selectbox("Tırmanış Stili", stiller)
            zorluk = st.selectbox("Zorluk (UIAA)", zorluk_dereceleri)
            uzunluk = st.number_input("Rota Uzunluğu (m)", min_value=0)
            dusus = st.selectbox("Sert Düşüş Sayısı?", [0, 1, 2, 3], help="Sadece yüksek faktörlü düşüşleri girin.")
            malzeme = st.selectbox("Kullanılan Ana Ekipman", malzemeler)

        detay = st.text_area("Teknik Notlar")
        submit = st.form_submit_button("Hesapla ve Drive'a Kaydet")
        
        if submit:
            if sheet is not None:
                try:
                    toplam = uzunluk * 2
                    yeni_satir = [str(tarih), sektor, rota, stil, zorluk, kisi, uzunluk, toplam, malzeme, dusus]
                    sheet.append_row(yeni_satir)
                    st.success(f"Başarılı! {kisi} için veri işlendi.")
                    st.balloons()
                except Exception as e:
                    st.error(f"Kayıt hatası: {e}")
            else:
                st.error("Veritabanı bağlantısı yok!")

    # 📘 TEKNİK REHBER
    st.write("---")
    with st.expander("📘 Malzeme Kullanım ve Güvenlik Kılavuzu"):
        st.error("### ⚠️ Sert Düşüş Nedir?")
        st.write("Lider tırmanışta son emniyet noktasının üzerine çıkıp yaşanan sert sarsıntılı düşüşlerdir.")

elif sekme == "👤 Tırmanıcı Analizi":
    st.title("👤 Tırmanıcı Performans Verileri")
    secilen_kisi = st.selectbox("İsim Seçiniz:", kullanicilar)
    
    if not df.empty:
        # Sütun adı Google Sheet'teki ile aynı olmalı (Örn: 'Yukleyen' veya 'Tırmanıcı')
        # Bu kodda 'Tırmanıcı' verisi yeni_satir'ın 6. elemanı (index 5)
        k_df = df[df['Yukleyen'] == secilen_kisi] if 'Yukleyen' in df.columns else pd.DataFrame()
        
        if not k_df.empty:
            m1, m2, m3 = st.columns(3)
            m1.metric("Toplam Metraj", f"{k_df['Rota_Uz'].sum()} m")
            m2.metric("Toplam Sert Düşüş", f"{k_df['Dusus'].sum()} Adet")
            m3.metric("Son Zorluk", k_df['Zorluk'].iloc[-1])
            st.dataframe(k_df, use_container_width=True)
        else:
            st.info("Bu tırmanıcıya ait henüz bir kayıt bulunamadı.")

elif sekme == "🛠 Malzeme Karnesi":
    st.title("🛠 Malzeme Sağlık Takibi")
    if not df.empty:
        ozet = df.groupby('Malzeme').agg({'Toplam_Ip': 'sum', 'Dusus': 'sum'})
        st.table(ozet)
