import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
from datetime import datetime

# 1. SAYFA AYARLARI
st.set_page_config(page_title="AKÜDAK Mezunları Portalı", layout="wide")

# 2. BAĞLANTI FONKSİYONU (SECRETS KULLANARAK)
def baglan(worksheet_index=0):
    try:
        # Streamlit Secrets'tan bilgileri çekiyoruz
        creds_dict = st.secrets["google_credentials"]
        creds = service_account.Credentials.from_service_account_info(
            creds_dict,
            scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        )
        client = gspread.authorize(creds)
        # Tablo adını da Secrets'tan alabiliriz
        return client.open(st.secrets["SPREADSHEET_ADI"]).get_worksheet(worksheet_index)
    except Exception as e:
        st.error(f"Bağlantı Hatası: {e}")
        return None

# 3. VERİLERİ ÇEKME
sheet = baglan(0)
if sheet:
    try:
        df = pd.DataFrame(sheet.get_all_records())
    except:
        df = pd.DataFrame()
else:
    df = pd.DataFrame()

# 4. YAN MENÜ
st.sidebar.title("🧭 AKÜDAK Menü")
sekme = st.sidebar.radio("Bölüm Seçin:", ["Ana Sayfa & Kayıt", "👤 Tırmanıcı Analizi", "🛠 Malzeme Karnesi"])

# --- ANA SAYFA & KAYIT ---
if sekme == "Ana Sayfa & Kayıt":
    st.title("🚀 AKÜDAK MEZUNLARI VERİ GİRİŞİ")
    
    with st.form("kayit_formu", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            kisi = st.selectbox("Tırmanıcı", ["Umut ŞEN", "Vedat AYDIN", "Mehmet AKŞİPAL", "Tanju DEMİREL", "Emre DOĞAN", "Misafir"])
            tarih = st.date_input("Tarih", datetime.now())
            rota = st.text_input("Rota Adı")
        with col2:
            uzunluk = st.number_input("Rota Uzunluğu (m)", min_value=0)
            malzeme = st.selectbox("Malzeme", ["Petzl Volta 9.0mm", "Ekspres Set", "Kemer"])
            dusus = st.selectbox("Düşüş Sayısı", [0, 1, 2, 3])

        submit = st.form_submit_button("Kaydet")
        
        if submit and sheet:
            try:
                yeni_satir = [str(tarih), rota, kisi, uzunluk, uzunluk*2, malzeme, dusus]
                sheet.append_row(yeni_satir)
                st.success("Veri başarıyla kaydedildi!")
                st.balloons()
            except Exception as e:
                st.error(f"Kayıt hatası: {e}")
