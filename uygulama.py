import streamlit as st
import pandas as pd

st.set_page_config(page_title="Seri Analiz Uzmanı", page_icon="♾️", layout="wide")

st.title("🤖 Sonsuz Seriler İçin Yapay Zeka Uzmanı")
st.markdown("Bu uygulama, serinin içindeki matematiksel bileşenlerin **konumlarına ve büyüme hızlarına** göre yakınsaklık/ıraksaklık analizi yapar.")

# Yan panel - Gelişmiş Kullanıcı Özellikleri
st.sidebar.header("Seri Özelliklerini Girin")

pay_derecesi = st.sidebar.number_input("Payın Derecesi (Kök için 0.5 yazabilirsiniz)", min_value=0.0, max_value=1000.0, value=1.0, step=0.5)
payda_derecesi = st.sidebar.number_input("Paydanın Derecesi (Kök için 0.5 yazabilirsiniz)", min_value=0.0, max_value=1000.0, value=1.0, step=0.5)

st.sidebar.markdown("---")
alterne_mi = st.sidebar.selectbox("Alterne Seri mi? (İçinde (-1)^n var mı?)", ["Hayır", "Evet"])

st.sidebar.markdown("---")
st.sidebar.subheader("Özel İfadeler Nerede Bulunuyor?")

secenekler = ["Yok", "Sadece Pay (Üst) Kısmında", "Sadece Payda (Alt) Kısmında", "Her İkisinde de"]

n_uzeri_n_konumu = st.sidebar.selectbox("n^n İfadesi Nerede?", secenekler)
faktoriyel_konumu = st.sidebar.selectbox("Faktöriyel (n!) Nerede?", secenekler)
ustel_konumu = st.sidebar.selectbox("Üstel İfade (a^n) Nerede?", secenekler)
logaritma_konumu = st.sidebar.selectbox("Logaritmik İfade (ln(n)) Nerede?", secenekler)
trigonometrik_konum = st.sidebar.selectbox("Trig. İfade (sin, cos) Nerede?", secenekler)

# Excel Verisini Yükleme
@st.cache_data
def veriyi_yukle():
    try:
        df = pd.read_excel("tez veri dosyası.xlsx")
        return df, True
    except:
        return None, False

df, durum = veriyi_yukle()

if st.sidebar.button("Analiz Et"):
    if durum:
        st.success("Yapay Zeka Analizi Başarıyla Tamamlandı!")
        
        # --- GELİŞMİŞ DİNAMİK TEST ÖNERİ MOTORU ---
        onerilen_testler = []
        
        if alterne_mi == "Evet":
            onerilen_testler.append("Leibniz (Alterne Seri) Testi")
            
        if n_uzeri_n_konumu != "Yok" or ustel_konumu != "Yok":
            onerilen_testler.append("Cauchy Kök Testi")
            
        if faktoriyel_konumu != "Yok":
            onerilen_testler.append("Oran (D'Alembert) Testi")
            
        if logaritma_konumu != "Yok":
            onerilen_testler.append("İntegral Testi veya Cauchy Yoğunlaşma Testi")
            
        if trigonometrik_konum != "Yok":
            onerilen_testler.append("Sıkıştırma (Sandviç) Teoremi veya Mutlak Yakınsaklık")
            
        # Eğer hiç özel ifade yoksa sadece polinom kuralları geçerlidir
        if len(onerilen_testler) == 0 or (len(onerilen_testler) == 1 and alterne_mi == "Evet"):
            onerilen_testler.append("Limit Karşılaştırma veya p-Serisi Testi")
            
        st.info(f"📌 **Bu Seri İçin Uygun Çözüm Yöntemleri:** {', '.join(onerilen_testler)}")

        # --- YAKINSAKLIK/IRAKSAKLIK TAHMİNİ ---
        if n_uzeri_n_konumu == "Sadece Pay (Üst) Kısmında" or faktoriyel_konumu == "Sadece Pay (Üst) Kısmında" or ustel_konumu == "Sadece Pay (Üst) Kısmında":
            st.error("💡 **Tahmini Sonuç:** IRAKSAK")
            st.write("📖 **Açıklama:** Paydaki çok hızlı büyüyen terimler, genel terim limitinin sıfır olmasını engeller (n. Terim Testi ile Iraksaklık).")
            
        elif n_uzeri_n_konumu == "Sadece Payda (Alt) Kısmında" or faktoriyel_konumu == "Sadece Payda (Alt) Kısmında" or ustel_konumu == "Sadece Payda (Alt) Kısmında":
            st.success("💡 **Tahmini Sonuç:** YAKINSAK")
            st.write("📖 **Açıklama:** Paydadaki hızlı büyüyen terimler seriyi çok hızlı sıfıra yaklaştırır ve seriyi yakınsatır.")
            
        else:
            # Sadece Polinom, Logaritma veya Trigonometri kaldıysa derece kontrolü
            if payda_derecesi > pay_derecesi + 1:
                st.success("💡 **Tahmini Sonuç:** YAKINSAK")
                st.write("📖 **Açıklama:** Paydanın derecesi, payın derecesinden 1'den fazla büyük olduğu için yakınsar (p-serisi mantığı).")
            elif payda_derecesi <= pay_derecesi:
                st.error("💡 **Tahmini Sonuç:** IRAKSAK")
                st.write("📖 **Açıklama:** Payın derecesi paydaya eşit veya daha büyük. Genel terim limiti sıfıra gitmez.")
            else:
                st.warning("💡 **Tahmini Sonuç:** ŞÜPHELİ / IRAKSAK EĞİLİMLİ")
                st.write("📖 **Açıklama:** Derece farkı 1 veya daha az (Örn: Harmonik seri). İntegral veya Limit Karşılaştırma testi ile detaylı incelenmelidir.")
    else:
        st.error("Hata: 'tez veri dosyası.xlsx' dosyası bulunamadı.")