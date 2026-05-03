import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import copy
import base64

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AKÜDAK Mezunları Portalı",
    layout="wide"
)

# ---------------- SPLASH SCREEN ----------------
def splash_screen():
    try:
        with open("resim_2.png", "rb") as f:
            img = base64.b64encode(f.read()).decode()
    except:
        img = ""

    st.markdown(f"""
    <style>
    .splash {{
        background-color: black;
        height: 100vh;
        width: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        position: fixed;
        top: 0;
        left: 0;
        z-index: 9999;
    }}

    .text {{
        color: white;
        font-family: monospace;
        font-size: 22px;
        margin-top: 20px;
        letter-spacing: 2px;
    }}

    img {{
        width: 180px;
    }}
    </style>

    <div class="splash">
        <img src="data:image/png;base64,{img}">
        <div class="text">AKÜDAK, it's not a pipe!</div>
    </div>
    """, unsafe_allow_html=True)


# ---------------- SHOW SPLASH ONCE ----------------
if "loaded" not in st.session_state:
    splash_screen()
    st.session_state["loaded"] = True
    st.stop()


# ---------------- BACKGROUND ----------------
def set_background(image_file):
    try:
        with open(image_file, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()

        st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}

        .block-container {{
            background-color: rgba(255,255,255,0.88);
            padding: 2rem;
            border-radius: 12px;
        }}
        </style>
        """, unsafe_allow_html=True)
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


# ---------------- SIDEBAR ----------------
st.sidebar.title("🧭 AKÜDAK Menü")

page = st.sidebar.radio("Seçim", [
    "🚀 Ana Sayfa",
    "👤 Tırmanıcı Analizi",
    "🛠 Malzeme Karnesi"
])


# ---------------- DATA LISTS ----------------
kullanicilar = [
    "Umut ŞEN", "Vedat AYDIN", "Mehmet AKŞİPAL",
    "Tanju DEMİREL", "Yavuz S. ÇAMUR",
    "Emre DOĞAN", "Erhan YALÇIN"
]

stiller = ["Lider", "Top-Rope"]

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


# ---------------- PAGE 1 ----------------
def ana_sayfa():
    st.title("🚀 AKÜDAK VERİ GİRİŞİ")

    with st.form("form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            kisi = st.selectbox("Tırmanıcı", kullanicilar)
            tarih = st.date_input("Tarih", datetime.now())
            sektor = st.text_input("Sektör")
            rota = st.text_input("Rota")

        with col2:
            stil = st.selectbox("Stil", stiller)
            zorluk = st.selectbox("Zorluk", zorluk_dereceleri)
            uzunluk = st.number_input("Uzunluk", 0)
            dusus = st.selectbox("Düşüş", [0, 1, 2, 3])
            malzeme = st.selectbox("Ekipman", malzemeler)

        submit = st.form_submit_button("Kaydet")

        if submit:
            ip = uzunluk * 2

            sheet.append_row([
                str(tarih),
                sektor,
                rota,
                stil,
                zorluk,
                kisi,
                uzunluk,
                ip,
                malzeme,
                dusus
            ])

            st.success("Kayıt başarılı!")
            st.balloons()


# ---------------- PAGE 2 ----------------
def analiz():
    st.title("👤 Tırmanıcı Analizi")

    secilen = st.selectbox("Kişi", kullanicilar)

    if not df.empty and "Yukleyen" in df.columns:
        k = df[df["Yukleyen"] == secilen]

        if not k.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("Lider", k[k["Stil"] == "Lider"]["Rota_Uz"].sum())
            c2.metric("Top-Rope", k[k["Stil"] == "Top-Rope"]["Rota_Uz"].sum())
            c3.metric("Son Zorluk", str(k["Zorluk"].iloc[-1]))

            st.dataframe(k, use_container_width=True)


# ---------------- PAGE 3 ----------------
def malzeme():
    st.title("🛠 Malzeme Karnesi")

    if not df.empty:
        o = df.groupby("Malzeme").agg({
            "Toplam_Ip": "sum",
            "Dusus": "sum"
        })

        o.columns = ["Metraj", "Düşüş"]
        st.table(o)


# ---------------- ROUTER ----------------
if page == "🚀 Ana Sayfa":
    ana_sayfa()

elif page == "👤 Tırmanıcı Analizi":
    analiz()

elif page == "🛠 Malzeme Karnesi":
    malzeme()
