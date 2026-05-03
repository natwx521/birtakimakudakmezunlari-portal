import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import copy
import base64

# ---------------- PAGE SETUP ----------------
st.set_page_config(
    page_title="AKÜDAK Mezunları Portalı",
    layout="wide"
)

# ---------------- BACKGROUND ----------------
def set_background(image_file):
    with open(image_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
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

# 👉 background dosyan varsa aç
set_background("resim01.png")


# ---------------- GOOGLE CONNECTION ----------------
@st.cache_resource
def baglan():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds_dict = copy.deepcopy(dict(st.secrets["gcp_service_account"]))

    if "private_key" in creds_dict:
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


# ---------------- MENU ----------------
st.sidebar.title("🧭 AKÜDAK Menü")

sekme = st.sidebar.radio(
    "Bölüm",
    ["Ana Sayfa & Kayıt", "👤 Tırmanıcı Analizi", "🛠 Malzeme Karnesi"]
)

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


# ---------------- HOME ----------------
if sekme == "Ana Sayfa & Kayıt":
    st.title("🚀 AKÜDAK VERİ GİRİŞİ")

    # IP CHECK
    if not df.empty and "Malzeme" in df.columns:
        ip_df = df[df["Malzeme"].astype(str).str.contains("Volta", na=False)]

        if not ip_df.empty:
            toplam_metraj = ip_df["Toplam_Ip"].sum()
            toplam_dusus = ip_df["Dusus"].sum()

            st.subheader("🪢 İp Durumu")

            c1, c2, c3 = st.columns(3)
            c1.metric("Toplam Kullanım", f"{toplam_metraj} m")
            c2.metric("Sert Düşüş", toplam_dusus)

            durum = "GÜVENLİ ✅" if (toplam_dusus < 5 and toplam_metraj < 5000) else "RİSKLİ ⚠️"

            if "GÜVENLİ" in durum:
                c3.success(durum)
            else:
                c3.error(durum)

    st.divider()

    # FORM
    with st.form("kayit", clear_on_submit=True):
        st.subheader("📝 Yeni Faaliyet")

        col1, col2 = st.columns(2)

        with col1:
            kisi = st.selectbox("Tırmanıcı", kullanicilar)
            tarih = st.date_input("Tarih", datetime.now())
            sektor = st.text_input("Sektör")
            rota = st.text_input("Rota")

        with col2:
            stil = st.selectbox("Stil", stiller)
            zorluk = st.selectbox("Zorluk", zorluk_dereceleri)
            uzunluk = st.number_input("Uzunluk (m)", min_value=0)
            dusus = st.selectbox("Sert Düşüş", [0, 1, 2, 3])
            malzeme = st.selectbox("Ekipman", malzemeler)

        detay = st.text_area("Notlar")

        submit = st.form_submit_button("Kaydet")

        if submit:
            try:
                ip_kullanim = uzunluk * 2

                sheet.append_row([
                    str(tarih),
                    sektor,
                    rota,
                    stil,
                    zorluk,
                    kisi,
                    uzunluk,
                    ip_kullanim,
                    malzeme,
                    dusus
                ])

                st.success("Kayıt başarılı!")
                st.balloons()

            except Exception as e:
                st.error(f"Kayıt Hatası: {e}")


# ---------------- ANALYSIS ----------------
elif sekme == "👤 Tırmanıcı Analizi":
    st.title("👤 Analiz")

    secilen = st.selectbox("Kişi", kullanicilar)

    if not df.empty and "Yukleyen" in df.columns:
        k_df = df[df["Yukleyen"] == secilen]

        if not k_df.empty:
            c1, c2, c3 = st.columns(3)

            c1.metric("Lider", k_df[k_df["Stil"] == "Lider"]["Rota_Uz"].sum())
            c2.metric("Top-Rope", k_df[k_df["Stil"] == "Top-Rope"]["Rota_Uz"].sum())
            c3.metric("Son Zorluk", str(k_df["Zorluk"].iloc[-1]))

            st.dataframe(k_df, use_container_width=True)

        else:
            st.warning("Veri yok")


# ---------------- MATERIAL ----------------
elif sekme == "🛠 Malzeme Karnesi":
    st.title("🛠 Malzeme Takibi")

    if not df.empty:
        ozet = df.groupby("Malzeme").agg({
            "Toplam_Ip": "sum",
            "Dusus": "sum"
        })

        ozet.columns = ["Metraj", "Düşüş"]

        st.table(ozet)
