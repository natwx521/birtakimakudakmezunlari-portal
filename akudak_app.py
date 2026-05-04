import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, date
import copy
import base64
import time

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="bir takım AKÜDAK mezunları Portalı",
    layout="wide"
)

# ---------------- ANDROID SCROLL / REFRESH FIX ----------------
st.markdown("""
<style>
div[data-baseweb="select"] div {
    max-height: 350px !important;
}

div[role="listbox"] {
    max-height: 350px !important;
    overflow-y: auto !important;
    -webkit-overflow-scrolling: touch !important;
}
</style>
""", unsafe_allow_html=True)


# ---------------- SPLASH SCREEN ----------------
def splash_screen():
    try:
        with open("resim_2.png", "rb") as f:
            img = base64.b64encode(f.read()).decode()
    except:
        img = ""

    splash = st.empty()
    text = "_     It's not a pipe!!!  It's AKÜDAK....      _"
    typed = ""

    for i in range(len(text)):
        typed += text[i]

        splash.markdown(f"""
        <style>
        body {{
            background-color: black;
        }}
        .splash {{
            background-color: black;
            height: 100vh;
            width: 100%;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            align-items: center;
            color: red;
            padding-top: 80px;
        }}

        .text {{
            font-family: monospace;
            font-size: 24px;
            letter-spacing: 2px;
            margin-top: 20px;
        }}

        img {{
            width: 180px;
        }}
        </style>

        <div class="splash">
            <img src="data:image/png;base64,{img}">
            <div class="text">{typed}|</div>
        </div>
        """, unsafe_allow_html=True)

        time.sleep(0.14)

    time.sleep(1)
    splash.empty()


# ---------------- RUN SPLASH ONCE ----------------
if "loaded" not in st.session_state:
    splash_screen()
    st.session_state["loaded"] = True


# ---------------- BACKGROUND ----------------
def set_background(image_file):
    try:
        with open(image_file, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()

        css = f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}

        /* SIDEBAR BACKGROUND IMAGE */
        section[data-testid="stSidebar"] {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
        }}

        /* LIGHT MODE */
        @media (prefers-color-scheme: light) {{
            .block-container {{
                background-color: rgba(255,255,255,0.88);
                color: black;
            }}
        }}

        /* DARK MODE */
        @media (prefers-color-scheme: dark) {{
            .block-container {{
                background-color: rgba(0,0,0,0.75);
                color: white;
            }}
        }}
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
    except:
        pass

set_background("resim01.png")


# ---------------- GOOGLE SHEET ----------------
@st.cache_resource
def baglan():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds_dict = copy.deepcopy(dict(st.secrets["gcp_service_account"]))
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")

    creds = Credentials.from_service_account_info(
        creds_dict,
        scopes=scope
    )

    client = gspread.authorize(creds)
    return client.open("faaliyet_kayitlari").sheet1


# ---------------- DATA ----------------
try:
    sheet = baglan()
    df = pd.DataFrame(sheet.get_all_records())
except Exception as e:
    st.error(f"Bağlantı Hatası: {e}")
    df = pd.DataFrame()


def ip_kullanim_hesapla():
    if df.empty:
        return 0, 0

    if "Toplam_Ip" in df.columns and "Dusus" in df.columns:
        toplam_metraj = df["Toplam_Ip"].sum()
        toplam_dusus = df["Dusus"].sum()
        return toplam_metraj, toplam_dusus

    return 0, 0


# ---------------- SIDEBAR ----------------
page = st.sidebar.radio("Seçim", [
    "🏠 ANA SAYFA",
    "🏔️ VERİ GİRİŞİ",
    "🧗 Tırmanıcı Analizi",
    "🛠 Malzeme Karnesi"
])


# ---------------- DATA LISTS ----------------
kullanicilar = [
    "Umut ŞEN", "Vedat AYDIN", "Mehmet AKŞİPAL",
    "Tanju DEMİREL", "Yavuz S. ÇAMUR",
    "Emre DOĞAN", "Erhan YALÇIN", "Misafir"
]

stiller = ["LiderSpor", "LiderTRAD", "Top-Rope"]

zorluk_dereceleri = [
    "IV", "V-", "V", "V+", "VI-", "VI", "VI+",
    "VII-", "VII", "VII+", "VIII-", "VIII",
    "VIII+", "IX-", "IX"
]

malzemeler = [
    "Petzl Volta Guide 9.0mm (80m)",
    "Corax LT Kemer M",
    "Corax LT Kemer XL",
    "Petzl Reverso Kırm.",
    "Petzl Reverso Yeşil.",
    "Ekspres Set"
]

# ... (devamı aynı)
