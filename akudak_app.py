import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# Secrets üzerinden bağlanma fonksiyonu
@st.cache_resource
def baglan():
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    # Streamlit'in kendi içindeki secrets yapısını kullanıyoruz
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    client = gspread.authorize(creds)
    return client.open('faaliyet_kayitlari').get_worksheet(0)

try:
    sheet = baglan()
    df = pd.DataFrame(sheet.get_all_records())
    st.success("Bağlantı Başarılı! 🧗‍♂️")
except Exception as e:
    st.error(f"Hata: {e}")
