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

# ---------------- ANDROID SCROLL / REFRESH FIX (ONLY ADDITION) ----------------
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

        time.sleep(0.18)

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

        .block-container {{
            background-color: rgba(255,255,255,0.88);
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


# ---------------- SIDEBAR ----------------
st.sidebar.title("🏔️ AKÜDAK Menü")

page = st.sidebar.radio("Seçim", [
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

# 🔥 EKLENEN: MALZEME SABİT LİSTE
malzeme_sabit = [
    {"ad": "Petzl Volta Guide 9.0mm (80m)", "tarih": "30.03.2026", "tip": "ip"},
    {"ad": "Corax LT Kemer M", "tarih": "30.03.2026", "tip": "tekstil"},
    {"ad": "Corax LT Kemer XL", "tarih": "30.03.2026", "tip": "tekstil"},
    {"ad": "Petzl Reverso Kırm.", "tarih": "30.03.2026", "tip": "metal"},
    {"ad": "Petzl Reverso Yeşil.", "tarih": "30.03.2026", "tip": "metal"},
    {"ad": "Ekspres Set", "tarih": "30.03.2026", "tip": "tekstil"}
]

# 🔥 EKLENEN: ÖMÜR HESAP
def omur_hesapla(tarih_str, tip, metraj=0, dusus=0):
    tarih = datetime.strptime(tarih_str, "%d.%m.%Y").date()
    yil = (date.today() - tarih).days / 365

    if tip == "metal":
        kalan = max(0, 1 - yil / 10)
    elif tip == "tekstil":
        kalan = max(0, 1 - yil / 10)
    elif tip == "ip":
        yas = yil / 10
        metraj_oran = metraj / 5000
        dusus_oran = dusus / 10
        kalan = max(0, 1 - (yas + metraj_oran + dusus_oran))

    return kalan

def renk(kalan):
    if kalan > 0.7:
        return "green"
    elif kalan > 0.4:
        return "orange"
    else:
        return "red"


# ---------------- PAGE 1 ----------------
def ana_sayfa():
    st.title("🏔️ AKÜDAK VERİ GİRİŞİ")

    # 🔥 EKLENEN: MALZEME ÖMÜR PANELİ
    st.subheader("🧗 Malzeme Durumu")

    for m in malzeme_sabit:
        kalan = omur_hesapla(m["tarih"], m["tip"], metraj=1000, dusus=1)

        st.write(f"**{m['ad']}**")
        st.progress(kalan)
        st.markdown(
            f"<div style='color:{renk(kalan)}'>%{int(kalan*100)} kalan</div>",
            unsafe_allow_html=True
        )

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
    st.title("🧗 Tırmanıcı Analizi")

    secilen = st.selectbox("Kişi", kullanicilar)

    if not df.empty and "Yukleyen" in df.columns:
        df["Yukleyen"] = df["Yukleyen"].astype(str).str.strip()

        if secilen == "Misafir":
            k = df.copy()
        else:
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
if page == "🏔️ VERİ GİRİŞİ":
    ana_sayfa()

elif page == "🧗 Tırmanıcı Analizi":
    analiz()

elif page == "🛠 Malzeme Karnesi":
    malzeme()
