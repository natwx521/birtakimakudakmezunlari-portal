import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# 1. SAYFA AYARLARI
st.set_page_config(page_title="AKÜDAK Mezunları Portalı", layout="wide")

# 2. BAĞLANTI AYARLARI
GOOGLE_JSON = {
    "type": "service_account",
    "project_id": "refined-helix-495108-d4",
    "private_key_id": "617a967a29b79d716b5d77a8419189d93dae2f3b",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQD6Ec9NaceIFmXQ\nra0E23cNFbh0dQUbgrI/yxGpghI3qy4wKtFBZ3E7ZhpahLCWJduGclOThSfh0NZK\nyhE2GmqERFpCcDLKv+w6QjBQZBeib4xrwAZ9jQkzwSC0THT7t+QXdlV0MQ7yV3/U\nX0Yl1YEHh7W+bXaNb8B+3+kzMytxTTUu8w9YwnOLc1qRyGP+YsE3nlARtSEACIZJ\n2ar6j9p3sAlMss/lFVFmii0bKbEZZgw/amgYWpVwMT0ASITH6xOWLVgbNt4OZMhf\nQn3UjbvH6khEzd/JbTZA7tXJK/jnPZcRCyHIX6tLE0hLJYCVfm0ctQH8Ghn35Bms\nWK7j6Vm5AgMBAAECggEAEphI7zN2rhimRQRpGXOdUGiFUQmTkeZfzU0TGOTuaFvP\nAS9p5IBl49oVixYTUHLrtj1hmBZebxT5nlGUwo5nzcKMaKTRrhBj5zgdQhkTRdWg\nHjIG+YaHgOTzQtztlPspV5JJy+xK9XvKqlbUT0NnRxFREyIuHtnIuVZ6j39WU2QZ\n95rVN+q353eJEmJ1XvC3za6SE9uqFMLa3jqwdXDkHqKQSKbRH2y4WJMF6/APOBIx\njlJIeZJu3ngUS7a59Tacj0TjXLWRbxgPtJ7M1rAb3mAmzOZA7rCKnQZt7FZ44cFm\nHFBkkwbmuGVMBghS5gBhq8jp95m8LyYo5qkZhIKWNQKBgQD9Pso2fxsZ2XB2ucg7\nOI+ssz+xJeEdG2eTQM+APA8LfQmJFNwk5gDBoVXiDEU0TUgZ4Im1kJaXaNCg8W98\nNhBPmdlpztI7n5FZQ1fU0ylUJSUI7Sgy0pQIVIYNWo0L12MhoWD/pmnnQQy9E4Gh\nLjbhXCdw4yCTJWRtavK5nPyoJQKBgQD8yi0wskIeO58Gd2FQ+ln+tWNmklPoIk3j\n1gqknF2Oe2H9nPGQGcLz2p4oamP8nPlxlqKrDVvFxcSdsoWu1e6U+d/vG4d39zYm\nzYNHrZFKSNksiInG6vpCKGXy7ekaM3EjxxO9skCwcT/Y1Cc0mxmz9NgEZ2F4zWlO\nDKFSm2B9BQKBgFSu2XmtuUdEkbnx2AYNnOW4LvUy4HsWPeVcx8Zuzu0di8G+Kvtf\ nuiMFqy1iwwWBTjnw/rurNOA+mX0oHwqfHYcwwCYElgKAEl+SCF3PmsNbhG3euBF+\nnyfF8+mlPQMXrDuDtmbmpAVDmFnlmvRl+s4TPdEe8jaiS1nXaIEvAMHNAoGBANB2\nda/LwOSnrCur9Q/PdLmsoc0rbJBpAayajWpUHH7sVtHLRBXeeLuaFIUlv1DJrpcy\nbvD6ciz1O4AEgWO9viMSsM3A+QVAU2LKZbGNe9wzmQy1iFEG49v87p3X/jwCIhIs\nEKaFwfz/V3Sa973VDewuRJnVGzeAxY98sOirg3V1AoGBAPu1EjQHe0ZQWSmRqupN\nMpqg0YsIoge/kO/fw01zPkq0Ai8aCXbV0nyxmh91qvKPlUSgiuHsvS8Q2EvEDv4N\nsf+3/PlUTcq3iY0puQff2CkA9nZKLRLjfs3netDtiGZxqAerrLUahXfNkrveaKWM\ntfkBU2DUqA27j2xYGSe2N0cW\n-----END PRIVATE KEY-----\n",
    "client_email": "mezun-takip@refined-helix-495108-d4.iam.gserviceaccount.com",
    "client_id": "104958170885135111051",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/mezun-takip%40refined-helix-495108-d4.iam.gserviceaccount.com"
}

# Private key temizliği
GOOGLE_JSON["private_key"] = GOOGLE_JSON["private_key"].replace("\\n", "\n")

# Caching (Önbellekleme) ekledik: Bu, dönen imlecin en büyük düşmanıdır.
@st.cache_resource
def get_sheet():
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_info(GOOGLE_JSON, scopes=scope)
    client = gspread.authorize(creds)
    return client.open('faaliyet_kayitlari').get_worksheet(0)

# Veriyi çekme
try:
    sheet = get_sheet()
    df = pd.DataFrame(sheet.get_all_records())
except Exception as e:
    st.error(f"Bağlantı Kurulamadı: {e}")
    df = pd.DataFrame()

# 3. SIDEBAR
st.sidebar.title("🧭 AKÜDAK Menü")
sekme = st.sidebar.radio("Bölüm Seç:", ["Kayıt Paneli", "Analiz & Malzeme"])

kullanicilar = ["Umut ŞEN", "Vedat AYDIN", "Mehmet AKŞİPAL", "Tanju DEMİREL", "Yavuz S. ÇAMUR", "Emre DOĞAN", "Erhan YALÇIN"]
malzemeler = ["Petzl Volta Guide 9.0mm (80m)", "Corax LT Kemer", "Ekspres Set"]

if sekme == "Kayıt Paneli":
    st.title("🚀 AKÜDAK Veri Girişi")
    
    with st.form("kayit_formu"):
        col1, col2 = st.columns(2)
        with col1:
            kisi = st.selectbox("Tırmanıcı", kullanicilar)
            tarih = st.date_input("Tarih", datetime.now())
            rota = st.text_input("Rota")
        with col2:
            uzunluk = st.number_input("Metraj (m)", min_value=0)
            dusus = st.selectbox("Sert Düşüş", [0, 1, 2, 3])
            malzeme = st.selectbox("Malzeme", malzemeler)
            
        submit = st.form_submit_button("Kaydet")
        
        if submit:
            try:
                # Toplam ip kullanımı = gidiş-dönüş (uzunluk * 2)
                yeni_satir = [str(tarih), "Genel", rota, "Lider", "VI", kisi, uzunluk, uzunluk*2, malzeme, dusus]
                sheet.append_row(yeni_satir)
                st.success("Kayıt Başarılı!")
                st.rerun()
            except Exception as e:
                st.error(f"Hata: {e}")

    if not df.empty:
        st.write("### Son Kayıtlar")
        st.dataframe(df.tail(5))

else:
    st.title("🛠 Analiz ve Malzeme Durumu")
    if not df.empty:
        # Basit malzeme özeti
        ozet = df.groupby('Malzeme').agg({'Toplam_Ip': 'sum', 'Dusus': 'sum'})
        st.table(ozet)
