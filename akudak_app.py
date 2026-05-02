import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# 1. SAYFA VE TEMA AYARLARI
st.set_page_config(page_title="AKÜDAK Mezunları Portalı", layout="wide")

# 2. BAĞLANTI AYARLARI (Orijinal Dosya Yöntemi)
JSON_KEY_DOSYASI = 'credentials.json'

# Önbellekleme: Dönen imleci ve uygulamanın kilitlenmesini engeller.
@st.cache_resource
def baglan():
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_file(JSON_KEY_DOSYASI, scopes=scope)
    client = gspread.authorize(creds)
    return client.open('faaliyet_kayitlari').get_worksheet(0)

# 3. VERİ ÇEKME
try:
    sheet = baglan()
    df = pd.DataFrame(sheet.get_all_records())
except Exception as e:
    st.error(f"Bağlantı Kurulamadı. JSON dosyasının GitHub'da yüklü olduğundan emin ol. Detay: {e}")
    df = pd.DataFrame()

# 4. YAN MENÜ (SIDEBAR)
st.sidebar.title("🧭 AKÜDAK Menü")
sekme = st.sidebar.radio("Gitmek İstediğiniz Bölüm:", ["Ana Sayfa & Kayıt", "👤 Tırmanıcı Analizi", "🛠 Malzeme Karnesi"])

# SABİT LİSTELER
kullanicilar = ["Umut ŞEN", "Vedat AYDIN", "Mehmet AKŞİPAL", "Tanju DEMİREL", "Yavuz S. ÇAMUR", "Emre DOĞAN", "Erhan YALÇIN"]
stiller = ["Lider", "Top-Rope"]
zorluk_dereceleri = ["IV", "V-", "V", "V+", "VI-", "VI", "VI+", "VII-", "VII", "VII+", "VIII-", "VIII", "VIII+", "IX-", "IX"]
malzemeler = ["Petzl Volta Guide 9.0mm (80m)", "Corax LT Kemer M", "Corax LT Kemer XL", "Petzl Reverso Kırm.", "Petzl Reverso Yeşil.", "Ekspres Set"]

# --- SEKMELER ---

if sekme == "Ana Sayfa & Kayıt":
    st.title("🚀 AKÜDAK MEZUNLARI VERİ GİRİŞİ")
    
    # 🪢 ANA İP DURUM PANELİ
    if not df.empty and "Malzeme" in df.columns:
        ip_df = df[df['Malzeme'].str.contains("Volta", na=False)]
        if not ip_df.empty:
            toplam_metraj = ip_df['Toplam_Ip'].sum()
            toplam_dusus = ip_df['Dusus'].sum()
            
            st.subheader("🪢 1 No'lu İp Durumu (Petzl Volta 80m)")
            c1, c2, c3 = st.columns(3)
            c1.metric("Toplam Kullanım", f"{toplam_metraj} m")
            c2.metric("Sert Düşüş", f"{toplam_dusus} Adet")
            
            is_safe = "GÜVENLİ ✅" if toplam_dusus < 5 and toplam_metraj < 5000 else "RİSKLİ / KONTROL ET ⚠️"
            if is_safe == "GÜVENLİ ✅":
                c3.success(f"Emniyet Durumu: {is_safe}")
            else:
                c3.error(f"Emniyet Durumu: {is_safe}")
    
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
            dusus = st.selectbox("Sert Düşüş Sayısı?", [0, 1, 2, 3])
            malzeme = st.selectbox("Kullanılan Ana Ekipman", malzemeler)

        detay = st.text_area("Teknik Notlar")
        submit = st.form_submit_button("Hesapla ve Drive'a Kaydet")
        
        if submit:
            try:
                toplam_ip_kullanimi = uzunluk * 2
                yeni_satir = [str(tarih), sektor, rota, stil, zorluk, kisi, uzunluk, toplam_ip_kullanimi, malzeme, dusus]
                sheet.append_row(yeni_satir)
                st.success(f"Başarılı! {kisi} için {toplam_ip_kullanimi}m ip kullanımı işlendi.")
                st.balloons()
            except NameError:
                st.error("Bağlantı hatası: Sayfayı yenileyip tekrar deneyin.")
            except Exception as e:
                st.error(f"Kayıt Hatası: {e}")

    # 📘 GENİŞLETİLMİŞ TEKNİK REHBER
    with st.expander("📘 Malzeme Kullanım ve Güvenlik Kılavuzu"):
        st.error("### ⚠️ Sert Düşüş Nedir?")
        st.write("Lider tırmanışta son emniyet noktasının üzerine çıkılıp boşlukta uçulan durumdur.")
        st.info("### 🕒 İp Emeklilik Kriterleri")
        st.markdown("* Toplam 5000m tırmanış veya 5 sert düşüş sonrası ip emekliye ayrılmalıdır.")

elif sekme == "👤 Tırmanıcı Analizi":
    st.title("👤 Tırmanıcı Performans Verileri")
    secilen_kisi = st.selectbox("İsim Seçiniz:", kullanicilar)
    
    if not df.empty:
        k_df = df[df['Yukleyen'] == secilen_kisi]
        if not k_df.empty:
            m1, m2, m3 = st.columns(3)
            m1.metric("Toplam Lider", f"{k_df[k_df['Stil'] == 'Lider']['Rota_Uz'].sum()} m")
            m2.metric("Toplam Top-Rope", f"{k_df[k_df['Stil'] == 'Top-Rope']['Rota_Uz'].sum()} m")
            m3.metric("Son Zorluk Derecesi", str(k_df['Zorluk'].iloc[-1]))
            st.dataframe(k_df, use_container_width=True)
        else:
            st.warning("Bu kullanıcıya ait veri bulunamadı.")

elif sekme == "🛠 Malzeme Karnesi":
    st.title("🛠 Malzeme Sağlık Takibi")
    if not df.empty:
        ozet = df.groupby('Malzeme').agg({'Toplam_Ip': 'sum', 'Dusus': 'sum'}).rename(columns={'Toplam_Ip': 'Toplam Metraj (m)', 'Dusus': 'Toplam Sert Düşüş'})
        st.table(ozet)
