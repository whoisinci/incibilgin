import streamlit as st
from datetime import datetime

st.set_page_config(page_title="ENKA Olimpiyat Sistemi", layout="wide")

# --- ENKA BİRLEŞİK SINIF YAPISI ---
ENKA_SINIFLAR = [
    "Hazırlık A", "Hazırlık B", 
    "9AB", "9CD", "9EF", "9GH", "9FEN",
    "10AB", "10CD", "10EF", "10GH", "10FEN",
    "11AB", "11CD", "11EF", "11GH", "11FEN",
    "12A", "12B", "12C","12D","12E","12F","12G","12H"
]

# --- VERİ YÖNETİMİ ---
if 'users' not in st.session_state:
    st.session_state.users = {
        "enkaöğretmen1": {"pass": "51423", "role": "Ayşe Hoca", "ad": "Ayşe Hoca"},
        "enkaöğretmen2": {"pass": "42351", "role": "Çağla Hanım", "ad": "Çağla Hanım"}
    }
if 'sinif_programlari' not in st.session_state:
    st.session_state.sinif_programlari = {} 
if 'db_talepler' not in st.session_state:
    st.session_state.db_talepler = []
if 'logged_in_user' not in st.session_state:
    st.session_state.logged_in_user = None

def gun_ismini_bul(tarih_obj):
    gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
    return gunler[tarih_obj.weekday()]

# --- GİRİŞ / KAYIT EKRANI ---
if st.session_state.logged_in_user is None:
    tab1, tab2 = st.tabs(["🔐 Giriş Yap", "📝 Öğrenci Kayıt Ol"])
    with tab1:
        u_name = st.text_input("Okul Numarası / Kullanıcı Adı")
        u_pass = st.text_input("Şifre", type="password")
        if st.button("Sisteme Gir"):
            if u_name in st.session_state.users and st.session_state.users[u_name]["pass"] == u_pass:
                st.session_state.logged_in_user = u_name
                st.rerun()
            else:
                st.error("Giriş başarısız!")
    with tab2:
        st.subheader("Yeni Öğrenci Kaydı")
        yeni_ad = st.text_input("Ad Soyad")
        yeni_no = st.text_input("Okul Numarası")
        yeni_sifre = st.text_input("Şifre Belirleyin", type="password")
        yeni_sinif = st.selectbox("Sınıfınız", ENKA_SINIFLAR)
        
        st.divider()
        program = {}
        gunler_liste = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]

        sinif_kayitli_mi = yeni_sinif in st.session_state.sinif_programlari
        if sinif_kayitli_mi:
            st.info(f"💡 {yeni_sinif} programı sistemden otomatik getirildi.")
        
        for gun in gunler_liste:
            with st.expander(f"{gun} Programı"):
                gunun_dersleri = []
                for i in range(1, 10):
                    varsayilan_ders = ""
                    if sinif_kayitli_mi:
                        hazir_program = st.session_state.sinif_programlari[yeni_sinif]
                        if gun in hazir_program:
                            varsayilan_ders = hazir_program[gun][i-1]
                    ders_input = st.text_input(f"{gun} {i}. Ders", value=varsayilan_ders, key=f"reg_{yeni_sinif}_{gun}_{i}")
                    gunun_dersleri.append(ders_input)
                program[gun] = gunun_dersleri

        if st.button("Kaydı Tamamla"):
            if yeni_ad and yeni_no and yeni_sifre:
                st.session_state.users[yeni_no] = {"pass": yeni_sifre, "ad": yeni_ad, "role": "Öğrenci", "sinif": yeni_sinif, "program": program}
                st.session_state.sinif_programlari[yeni_sinif] = program
                st.success("Kayıt başarılı!")
            else:
                st.error("Eksik alan bırakmayın!")

else:
    u_id = st.session_state.logged_in_user
    u_data = st.session_state.users[u_id]
    
    st.sidebar.info(f"👤 {u_data['ad']}\n📅 {datetime.now().strftime('%d.%m.%Y')}")
    
    with st.sidebar.expander("⚙️ Hesap Ayarları"):
        yeni_kullanici_adi = st.text_input("Yeni Kullanıcı Adı (Okul No)", value=u_id)
        yeni_sifre_giris = st.text_input("Yeni Şifre", type="password", value=u_data["pass"])
        if st.button("Güncelle"):
            if yeni_kullanici_adi != u_id:
                st.session_state.users[yeni_kullanici_adi] = st.session_state.users.pop(u_id)
                st.session_state.logged_in_user = yeni_kullanici_adi
            st.session_state.users[st.session_state.logged_in_user]["pass"] = yeni_sifre_giris
            st.success("Bilgiler güncellendi!")
            st.rerun()

    if st.sidebar.button("🚪 Çıkış Yap"):
        st.session_state.logged_in_user = None
        st.rerun()

    # --- ÖĞRENCİ PANELİ ---
    if u_data["role"] == "Öğrenci":
        st.header("📋 Olimpiyat İzin Talebi")
        secili_tarih_ogrenci = st.date_input("İzin İstediğiniz Tarihi Seçin:", datetime.now())
        secili_gun_ismi = gun_ismini_bul(secili_tarih_ogrenci)
        formatli_tarih_ogrenci = secili_tarih_ogrenci.strftime("%d/%m/%Y")
        
        st.write(f"Seçilen Gün: **{secili_gun_ismi}**")

        kendi_talepleri = [t for t in st.session_state.db_talepler if t["no"] == u_id]
        if kendi_talepleri:
            with st.expander("📌 Taleplerimin Durumu"):
                for kt in kendi_talepleri:
                    renk = "green" if kt['durum'] == "Onaylandı" else "red" if kt['durum'] == "Reddedildi" else "orange"
                    st.markdown(f"Tarih: {kt['tarih']} ({kt['gun']}) | Durum: :{renk}[{kt['durum']}]")

        st.divider()
        if secili_gun_ismi in ["Cumartesi", "Pazar"]:
            st.warning("Hafta sonu için izin talebi oluşturulamaz.")
        else:
            secili_nolar = st.multiselect("Hangi Ders Saatlerinde Çıkacaksınız?", list(range(1, 10)))
            if st.button("Talebi Gönder"):
                zaten_var = any(t['no'] == u_id and t['tarih'] == formatli_tarih_ogrenci for t in st.session_state.db_talepler)
                if zaten_var:
                    st.warning(f"⚠️ {formatli_tarih_ogrenci} tarihi için zaten bir talebiniz bulunuyor.")
                elif not secili_nolar:
                    st.error("Lütfen ders saati seçin.")
                else:
                    d_adlari = [u_data["program"][secili_gun_ismi][n-1] for n in secili_nolar]
                    st.session_state.db_talepler.append({
                        "isim": u_data["ad"], "no": u_id, "sinif": u_data["sinif"],
                        "gun": secili_gun_ismi, "ders_nolar": secili_nolar, "ders_adlari": d_adlari,
                        "durum": "Bekliyor", "tarih": formatli_tarih_ogrenci
                    })
                    st.success(f"{formatli_tarih_ogrenci} günü için talebiniz iletildi.")

    # --- AYŞE HOCA PANELİ ---
    elif u_data["role"] == "Ayşe Hoca":
        st.header("🔑 Ayşe Hoca Yönetim Paneli")
        secili_tarih_hoca = st.date_input("Görüntülenecek Tarih:", datetime.now())
        formatli_tarih_hoca = secili_tarih_hoca.strftime("%d/%m/%Y")
        
        tab_onay, tab_arsiv, tab_ogrenci_listesi = st.tabs(["📥 Bekleyen Talepler", "📜 Onaylı Liste & WhatsApp", "👥 Öğrenci Yönetimi"])
        
        with tab_onay:
            bekleyenler = [t for t in st.session_state.db_talepler if t["durum"] == "Bekliyor" and t["tarih"] == formatli_tarih_hoca]
            if bekleyenler:
                if st.button("✨ Tümünü Onayla"):
                    for t in st.session_state.db_talepler:
                        if t["durum"] == "Bekliyor" and t["tarih"] == formatli_tarih_hoca:
                            t["durum"] = "Onaylandı"
                    st.success("Talepler onaylandı!")
                    st.rerun()
                
                st.divider()
                for idx, talep in enumerate(st.session_state.db_talepler):
                    if talep["durum"] == "Bekliyor" and talep["tarih"] == formatli_tarih_hoca:
                        c1, c2, c3 = st.columns([3, 1, 1])
                        # DÜZELTİLEN KISIM: Ders numarası ve adı yan yana yazıldı.
                        ders_ozeti = ", ".join([f"{n}. Ders ({ad})" for n, ad in zip(talep['ders_nolar'], talep['ders_adlari'])])
                        c1.markdown(f"**{talep['isim']} ({talep['sinif']})**")
                        c1.caption(f"Dersler: {ders_ozeti}")
                        if c2.button("✅ Onayla", key=f"app_{idx}"):
                            talep["durum"] = "Onaylandı"
                            st.rerun()
                        if c3.button("❌ Reddet", key=f"rej_{idx}"):
                            talep["durum"] = "Reddedildi"
                            st.rerun()
            else:
                st.info(f"{formatli_tarih_hoca} için bekleyen talep yok.")

        with tab_arsiv:
            onaylilar = [t for t in st.session_state.db_talepler if t["durum"] == "Onaylandı" and t["tarih"] == formatli_tarih_hoca]
            if onaylilar:
                for t in onaylilar:
                    st.write(f"✅ {t['isim']} ({t['sinif']}) - {t['ders_nolar']}. Dersler")
                
                st.divider()
                metin = f"*ENKA Olimpiyat İzinli Listesi ({formatli_tarih_hoca})*\n\n"
                for t in onaylilar:
                    metin += f"• {t['isim']} ({t['sinif']}) - Ders: {t['ders_nolar']}\n"
                st.text_area("WhatsApp Metni:", metin, height=150)
            else:
                st.write("Bu tarihte onaylanmış kimse bulunmuyor.")

        with tab_ogrenci_listesi:
            st.subheader("Sistemdeki Kayıtlı Öğrenciler")
            ogrenciler = {k: v for k, v in st.session_state.users.items() if v["role"] == "Öğrenci"}
            for oid, oinfo in ogrenciler.items():
                col1, col2 = st.columns([4, 1])
                col1.write(f"👤 **{oinfo['ad']}** (No: {oid}) - {oinfo['sinif']}")
                if col2.button("🗑️ Sil", key=f"del_user_{oid}"):
                    del st.session_state.users[oid]
                    st.warning(f"{oinfo['ad']} silindi.")
                    st.rerun()

    # --- ÇAĞLA HANIM PANELİ ---
    elif u_data["role"] == "Çağla Hanım":
        st.header("📝 Çağla Hanım - Devamsızlık")
        secili_tarih_cagla = st.date_input("Tarih Seçin:", datetime.now())
        formatli_tarih_cagla = secili_tarih_cagla.strftime("%d/%m/%Y")
        onaylilar = [t for t in st.session_state.db_talepler if t["durum"] == "Onaylandı" and t["tarih"] == formatli_tarih_cagla]
        if onaylilar:
            for t in onaylilar:
                with st.expander(f"✅ {t['isim']} ({t['sinif']})"):
                    st.write(f"No: {t['no']}")
                    for n, ad in zip(t['ders_nolar'], t['ders_adlari']):
                        st.write(f"- {n}. Ders: {ad}")
        else:
            st.info("Kayıt bulunamadı.")
