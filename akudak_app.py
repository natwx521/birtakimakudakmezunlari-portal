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
    backdrop-filter: blur(0px);
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
        return df["Toplam_Ip"].sum(), df["Dusus"].sum()

    return 0, 0


page = st.sidebar.radio("Seçim", [
    "🏠 ANA SAYFA",
    "🏔️ VERİ GİRİŞİ",
    "🧗 Tırmanıcı Analizi",
    "🛠 Malzeme Karnesi"
])

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

malzeme_sabit = [
    {"ad": "Petzl Volta Guide 9.0mm (80m)", "tarih": "30.03.2026", "tip": "ip"},
    {"ad": "Corax LT Kemer M", "tarih": "30.03.2026", "tip": "tekstil"},
    {"ad": "Corax LT Kemer XL", "tarih": "30.03.2026", "tip": "tekstil"},
    {"ad": "Petzl Reverso Kırm.", "tarih": "30.03.2026", "tip": "metal"},
    {"ad": "Petzl Reverso Yeşil.", "tarih": "30.03.2026", "tip": "metal"},
    {"ad": "Ekspres Set", "tarih": "30.03.2026", "tip": "tekstil"}
]


def omur_hesapla(tarih_str, tip, metraj=0, dusus=0):
    tarih = datetime.strptime(tarih_str, "%d.%m.%Y").date()
    yil = (date.today() - tarih).days / 365

    if tip in ["metal", "tekstil"]:
        return max(0, 1 - yil / 10)

    if tip == "ip":
        return max(0, 1 - ((yil/10) + metraj/5000 + dusus/10))

    return 0


def renk(kalan):
    return "green" if kalan > 0.7 else "orange" if kalan > 0.3 else "red"


def analiz():
    st.title("🧗 Tırmanıcı Analizi")

    # 🔥 TEK DEĞİŞİKLİK BURADA (SEARCHABLE + yazınca filtre)
    secilen = st.selectbox(
        "Kişi (yazmaya başla)",
        options=kullanicilar,
        index=None,
        placeholder="İsim yaz..."
    )

    if not secilen:
        return

    if not df.empty and "Yukleyen" in df.columns:

        df["Yukleyen"] = df["Yukleyen"].fillna("").astype(str).str.strip()

        if secilen == "Misafir":
            k = df.copy()
        else:
            k = df[df["Yukleyen"] == secilen]

        if secilen == "Misafir" and k.empty:
            k = df.copy()

        if not k.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("Lider", 0)
            c2.metric("Top-Rope", 0)
            c3.metric("Son Zorluk", str(k["Zorluk"].iloc[-1]) if "Zorluk" in k.columns else "-")

            st.dataframe(k, use_container_width=True)


def ana_sayfa():
    st.title("🏔️ AKÜDAK MEZUN ANA EKRAN")
    ip_metraj, ip_dusus = ip_kullanim_hesapla()

    for m in malzeme_sabit:
        kalan = omur_hesapla(m["tarih"], m["tip"], ip_metraj, ip_dusus)
        st.write(m["ad"])
        st.progress(kalan)


def veri_giris():
    st.title("VERİ GİRİŞİ")
    st.write("OK")


def malzeme():
    st.title("MALZEME")
    st.write("OK")


if page == "🏠 ANA SAYFA":
    ana_sayfa()
elif page == "🏔️ VERİ GİRİŞİ":
    veri_giris()
elif page == "🧗 Tırmanıcı Analizi":
    analiz()
elif page == "🛠 Malzeme Karnesi":
    malzeme()
