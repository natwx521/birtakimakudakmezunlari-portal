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
html, body {
    overscroll-behavior: none !important;
    -webkit-overflow-scrolling: touch;
}

[data-testid="stAppViewContainer"] {
    overscroll-behavior: none !important;
    touch-action: pan-y !important;
}

input, textarea, select {
    scroll-margin: 100px;
}

body {
    overscroll-behavior-y: contain;
}

/* 🔥 DROPDOWN UZATMA FIX */
div[data-baseweb="select"] ul {
    max-height: 500px !important;
    overflow-y: auto !important;
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
    text = "_     It's not a pipe!!!  It's AKÜDAK...      _"
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

        with open("resim03.png", "rb") as f2:
            sidebar_encoded = base64.b64encode(f2.read()).decode()

        css = f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}

        section[data-testid="stSidebar"] {{
            background-image: url("data:image/png;base64,{sidebar_encoded}");
            background-size: cover;
            background-position: center;
        }}

        section[data-testid="stSidebar"] > div {{
            background-color: rgba(255, 255, 255, 0.5) !important;
        }}

        .block-container {{
            background-color: rgba(255,255,255,0.3);
            padding: 2rem;
            border-radius: 12px;
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


# ---------------- METRAJ ----------------
def ip_kullanim_hesapla():
    if df.empty:
        return 0, 0

    if "Toplam_Ip" in df.columns and "Dusus" in df.columns:
        return df["Toplam_Ip"].sum(), df["Dusus"].sum()

    return 0, 0


# ---------------- SIDEBAR ----------------
page = st.sidebar.radio("Seçim", [
    "🏠 ANA SAYFA",
    "🏔️ VERİ GİRİŞİ",
    "🧗 Tırmanıcı Analizi",
    "🛠 Malzeme Karnesi"
])


# 🔥 FIX: Misafir en altta garanti
kullanicilar = sorted([
    "Umut ŞEN", "Vedat AYDIN", "Mehmet AKŞİPAL",
    "Tanju DEMİREL", "Yavuz S. ÇAMUR",
    "Emre DOĞAN", "Erhan YALÇIN", "Misafir"
], key=lambda x: (x == "Misafir", x))


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


# ---------------- ÖMÜR ----------------
def omur_hesapla(tarih_str, tip, metraj=0, dusus=0):
    tarih = datetime.strptime(tarih_str, "%d.%m.%Y").date()
    yil = (date.today() - tarih).days / 365

    if tip in ["metal", "tekstil"]:
        return max(0, 1 - yil / 10)

    if tip == "ip":
        return max(0, 1 - (yil/10 + metraj/5000 + dusus/10))

    return 1


def renk(kalan):
    return "green" if kalan > 0.7 else "orange" if kalan > 0.3 else "red"


# ---------------- PAGE 2 (FIX IMPORTANT PART) ----------------
def veri_giris():
    st.title("🏔️ AKÜDAK MEZUN VERİ GİRİŞİ")

    with st.form("form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            kisi = st.selectbox("Tırmanıcı", kullanicilar)

        with col2:
            stil = st.selectbox("Stil", stiller)

        tarih = st.date_input("Tarih", datetime.now())
        sektor = st.text_input("Sektör")
        rota = st.text_input("Rota")
        zorluk = st.selectbox("Zorluk", zorluk_dereceleri)
        uzunluk = st.number_input("Uzunluk", 0)
        dusus = st.selectbox("Düşüş", [0, 1, 2, 3])
        malzeme = st.selectbox("Ekipman", malzemeler)

        submit = st.form_submit_button("Kaydet")

        if submit:
            sheet.append_row([
                str(tarih),
                sektor,
                rota,
                stil,
                zorluk,
                kisi,
                uzunluk,
                uzunluk * 2,
                malzeme,
                dusus
            ])
            st.success("Kayıt başarılı!")


# ---------------- PAGE 3 FIX ----------------
def analiz():
    st.title("🧗 Tırmanıcı Analizi")

    secilen = st.selectbox("Kişi", kullanicilar)

    if not df.empty:
        df["Yukleyen"] = df.get("Yukleyen", "").astype(str).str.strip()

        k = df if secilen == "Misafir" else df[df["Yukleyen"] == secilen]

        if not k.empty:
            st.dataframe(k, use_container_width=True)


# ---------------- ROUTER ----------------
if page == "🏠 ANA SAYFA":
    st.write("OK")

elif page == "🏔️ VERİ GİRİŞİ":
    veri_giris()

elif page == "🧗 Tırmanıcı Analizi":
    analiz()

elif page == "🛠 Malzeme Karnesi":
    st.write("OK")
