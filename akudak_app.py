import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# 1. SAYFA VE TEMA AYARLARI
st.set_page_config(page_title="AKÜDAK Mezunları Portalı", layout="wide")

# 2. BAĞLANTI AYARLARI (Gömülü JSON Sistemi)
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
SPREADSHEET_ADI = 'faaliyet_kayitlari'

def baglan(worksheet_index=0):
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_info(GOOGLE_JSON, scopes=scope)
    client = gspread.authorize(creds)
    return client.open(SPREADSHEET_ADI).get_worksheet(worksheet_index)

# 3. VERİLERİ ÇEKME
try:
    sheet = baglan(0)
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
except Exception:
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
    st.title("🚀 AKÜDAK MEZUNLARI TEKNİK VERİ GİRİŞİ")
    
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
            dusus = st.selectbox(
                "Sert Düşüş Sayısı?", 
                [0, 1, 2, 3], 
                help="Sadece LİDER tırmanışta yaşanan şok yükleri girin."
            )
            malzeme = st.selectbox("Kullanılan Ana Ekipman", malzemeler)

        detay = st.text_area("Teknik Notlar")
        submit = st.form_submit_button("Hesapla ve Drive'a Kaydet")
        
        if submit:
            try:
                toplam_ip_kullanimi = uzunluk * 2
                # Google Sheets'e gidecek veri (Sıralama Sheets dosyanla aynı olmalı!)
                yeni_satir = [str(tarih), sektor, rota, stil, zorluk, kisi, uzunluk, toplam_ip_kullanimi, malzeme, dusus]
                sheet.append_row(yeni_satir)
                st.success(f"Başarılı! {kisi} için {toplam_ip_kullanimi}m ip kullanımı işlendi.")
                st.balloons()
            except Exception as e:
                st.error(f"Kayıt Hatası: {e}")

    # 📘 GENİŞLETİLMİŞ TEKNİK REHBER
    with st.expander("📘 Malzeme Kullanım ve Güvenlik Kılavuzu"):
        st.error("### ⚠️ Sert Düşüş Nedir?")
        st.write("Lider tırmanışta son emniyet noktasının üzerine çıkılıp boşlukta uçulan durumdur.")
        st.info("### 🕒 İp Emeklilik: 5000m veya 5 Sert Düşüş.")

elif sekme == "👤 Tırmanıcı Analizi":
    st.title("👤 Tırmanıcı Performans Verileri")
    secilen_kisi = st.selectbox("İsim Seçiniz:", kullanicilar)
    
    if not df.empty:
        k_df = df[df['Yukleyen'] == secilen_kisi]
        if not k_df.empty:
            m1, m2, m3 = st.columns(3)
            m1.metric("Toplam Lider", f"{k_df[k_df['Stil'] == 'Lider']['Rota_Uz'].sum()} m")
            m2.metric("Toplam Top-Rope", f"{k_df[k_df['Stil'] == 'Top-Rope']['Rota_Uz'].sum()} m")
            m3.metric("Son Zorluk", str(k_df['Zorluk'].iloc[-1]))
            st.dataframe(k_df, use_container_width=True)

elif sekme == "🛠 Malzeme Karnesi":
    st.title("🛠 Malzeme Sağlık Takibi")
    if not df.empty:
        ozet = df.groupby('Malzeme').agg({'Toplam_Ip': 'sum', 'Dusus': 'sum'})
        st.table(ozet)import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
from datetime import datetime

# 1. SAYFA VE TEMA AYARLARI
st.set_page_config(page_title="AKÜDAK Mezunları Portalı", layout="wide")

# 2. BAĞLANTI AYARLARI
JSON_KEY_DOSYASI = 'refined-helix-495108-d4-5b0da9922a2a.json'
SPREADSHEET_ADI = 'faaliyet_kayitlari'

def baglan(worksheet_index=0):
    creds = service_account.Credentials.from_service_account_file(
        JSON_KEY_DOSYASI, 
        scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    )
    client = gspread.authorize(creds)
    return client.open(SPREADSHEET_ADI).get_worksheet(worksheet_index)

# 3. VERİLERİ ÇEKME
try:
    sheet = baglan(0)
    df = pd.DataFrame(sheet.get_all_records())
except:
    df = pd.DataFrame()

# 4. YAN MENÜ (SIDEBAR)
st.sidebar.image("resim01.png", use_container_width=True)
st.sidebar.title("🧭 AKÜDAK Menü")
sekme = st.sidebar.radio("Gitmek İstediğiniz Bölüm:", ["Ana Sayfa & Kayıt", "👤 Tırmanıcı Analizi", "🛠 Malzeme Karnesi"])

# SABİT LİSTELER
kullanicilar = ["Umut ŞEN", "Vedat AYDIN", "Mehmet AKŞİPAL", "Tanju DEMİREL", "Yavuz S. ÇAMUR", "Emre DOĞAN", "Erhan YALÇIN"]
stiller = ["Lider", "Top-Rope"]
zorluk_dereceleri = ["IV", "V-", "V", "V+", "VI-", "VI", "VI+", "VII-", "VII", "VII+", "VIII-", "VIII", "VIII+", "IX-", "IX"]
malzemeler = ["Petzl Volta Guide 9.0mm (80m)", "Corax LT Kemer M", "Corax LT Kemer XL", "Petzl Reverso Kırm.", "Petzl Reverso Yeşil.", "Ekspres Set"]

# --- SEKMELER ---

if sekme == "Ana Sayfa & Kayıt":
    st.title("🚀 BİR TAKIM AKÜDAK MEZUNLARI VERİ GİRİŞİ")
    
    # 🪢 ANA İP DURUM PANELİ
    if not df.empty and "Petzl Volta" in df['Malzeme'].values:
        ip_df = df[df['Malzeme'].str.contains("Volta")]
        toplam_metraj = ip_df['Toplam_Ip'].sum()
        toplam_dusus = ip_df['Dusus'].sum()
        
        st.subheader("🪢 1 No'lu İp Durumu (Petzl Volta 80m)")
        c1, c2, c3 = st.columns(3)
        c1.metric("Toplam Kullanım", f"{toplam_metraj} m")
        c2.metric("Sert Düşüş", f"{toplam_dusus} Adet")
        
        is_safe = "GÜVENLİ ✅" if toplam_dusus < 5 and toplam_metraj < 5000 else "RİSKLİ / KONTROL ET ⚠️"
        c3.info(f"Emniyet Durumu: {is_safe}")
    
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
            # SERT DÜŞÜŞ SEÇİMİ (Yardım Metni Genişletildi)
            dusus = st.selectbox(
                "Sert Düşüş Sayısı?", 
                [0, 1, 2, 3], 
                help="Sadece LİDER tırmanışta yaşanan, ipin çok gerildiği yüksek düşüşleri girin. Top-rope düşüşlerini 0 girin."
            )
            malzeme = st.selectbox("Kullanılan Ana Ekipman", malzemeler)

        detay = st.text_area("Teknik Notlar")
        submit = st.form_submit_button("Hesapla ve Drive'a Kaydet")
        
        if submit:
            try:
                toplam = uzunluk * 2
                yeni_satir = [str(tarih), sektor, rota, stil, zorluk, kisi, uzunluk, toplam, malzeme, dusus]
                sheet.append_row(yeni_satir)
                st.success(f"Başarılı! {kisi} için {toplam}m ip kullanımı işlendi.")
                st.balloons()
            except Exception as e:
                st.error(f"Hata: {e}")

    # 📘 GENİŞLETİLMİŞ TEKNİK REHBER
    st.write("---")
    with st.expander("📘 Malzeme Kullanım ve Güvenlik Kılavuzu (MUTLAKA OKUYUN)"):
        st.error("### ⚠️ Sert Düşüş (Faktör Düşüşü) Nedir?")
        st.write("""
        Her düşüş sisteme sert düşüş olarak girilmez. Aşağıdaki senaryolara göre karar verin:
        *   **0 Girilecek Durumlar:** Top-rope tırmanırken düşmek, lider tırmanırken emniyet noktası göğüs hizasındayken 'oturmak' veya kısa (1 metreden az) düşüşler.
        *   **1+ Girilecek Durumlar:** Son ekspresin çok üzerine çıkıp boşlukta uçtuğunuz, ipin sizi sert bir sarsıntıyla tuttuğu veya emniyetçinin yukarı havalandığı 'şok' yüklü düşüşler.
        """)
        
        st.info("### 🕒 Malzeme Emeklilik Kriterleri")
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.markdown("""
            **Dinamik İpler:**
            *   Toplam 5000m tırmanış metrajı.
            *   Toplam 5 sert düşüş.
            *   Kılıfta kalıcı sertleşme veya çekirdek görünmesi.
            """)
        with col_r2:
            st.markdown("""
            **Metal Malzemeler:**
            *   Yüzeyde %10'dan fazla aşınma.
            *   Beton veya kaya zemine 2 metreden yüksekten düşme.
            *   Karabina kapılarının tam kapanmaması.
            """)

elif sekme == "👤 Tırmanıcı Analizi":
    st.title("👤 Tırmanıcı Performans Verileri")
    secilen_kisi = st.selectbox("İsim Seçiniz:", kullanicilar)
    
    if not df.empty:
        k_df = df[df['Yukleyen'] == secilen_kisi]
        if not k_df.empty:
            m1, m2, m3 = st.columns(3)
            m1.metric("Toplam Lider", f"{k_df[k_df['Stil'] == 'Lider']['Rota_Uz'].sum()} m")
            m2.metric("Toplam Top-Rope", f"{k_df[k_df['Stil'] == 'Top-Rope']['Rota_Uz'].sum()} m")
            m3.metric("Son Zorluk Derecesi", k_df['Zorluk'].iloc[-1])
            
            st.write("### 📅 Faaliyet Geçmişi")
            st.dataframe(k_df[['Tarih', 'Sektör', 'Rota', 'Stil', 'Zorluk', 'Rota_Uz', 'Dusus']], use_container_width=True)

elif sekme == "🛠 Malzeme Karnesi":
    st.title("🛠 Malzeme Sağlık ve Metraj Takibi")
    if not df.empty:
        ozet = df.groupby('Malzeme').agg({'Toplam_Ip': 'sum', 'Dusus': 'sum'}).rename(columns={'Toplam_Ip': 'Toplam Metraj (m)', 'Dusus': 'Toplam Sert Düşüş'})
        st.table(ozet)
