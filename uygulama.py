import streamlit as st
import pandas as pd

st.set_page_config(page_title="Seri Analiz Uzmanı", page_icon="♾️", layout="wide")

st.title("🤖 Sonsuz Seriler İçin Yapay Zeka Uzmanı")
st.markdown("Bu uygulama, serinin içindeki matematiksel bileşenlerin **konumlarına ve büyüme hızlarına** göre yakınsaklık/ıraksaklık analizi yapar.")

# Yan panel - Gelişmiş Kullanıcı Özellikleri
st.sidebar.header("Seri Özelliklerini Girin")

# Kökler (0.5 vb.) için ondalıklı (float) sayı desteği eklendi!
pay_derecesi = st.sidebar.number_input("Payın Derecesi (Kök için 0.5 yazabilirsiniz)", min_value=0.0, max_value=1000.0, value=1.0, step=0.5)
payda_derecesi = st.sidebar.number_input("Paydanın Derecesi (Kök için 0.5 yazabilirsiniz)", min_value=0.0, max_value=1000.0, value=1.0, step=0.5)

st.sidebar.markdown("---")
# Alterne Seri eklendi
alterne_mi = st.sidebar.selectbox("Alterne Seri mi? (İçinde (-1)^n var mı?)", ["Hayır", "Evet"])

st.sidebar.markdown("---")
st.sidebar.subheader("Özel İfadeler Nerede Bulunuyor?")

secenekler = ["Yok", "Sadece Pay (Üst) Kısmında", "Sadece Payda (Alt) Kısmında", "Her İkisinde de"]

# n^n eklendi ve en üste kondu (Çünkü en hızlı büyüyen o)
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
        
        # 1. Aşama: Alterne Seri Kontrolü
        if alterne_mi == "Evet":
            st.info("📌 **Seri Tipi:** Bu bir Alterne Seri (İşaret değiştiren seri).")
            st.write("💡 **Önerilen Test:** **Leibniz (Alterne Seri) Testi**. Mutlak yakınsaklık veya koşullu yakınsaklık durumları incelenmelidir.")
        
        # 2. Aşama: Büyüme Hiyerarşisi (n^n > n! > a^n)
        if n_uzeri_n_konumu == "Sadece Pay (Üst) Kısmında":
            st.error("💡 **Tahmini Sonuç:** IRAKSAK")
            st.info("📌 **Açıklama:** 'n^n' ifadesi matematikte en hızlı büyüyen terimdir. Payda kısmında ne olursa olsun, genel terimi sonsuza çeker. (Önerilen Test: Kök Testi)")
            
        elif n_uzeri_n_konumu == "Sadece Payda (Alt) Kısmında":
            st.success("💡 **Tahmini Sonuç:** YAKINSAK")
            st.info("📌 **Açıklama:** 'n^n' ifadesinin paydada olması, terimleri muazzam bir hızla sıfıra götürür ve seriyi yakınsatır. (Önerilen Test: Kök veya Oran Testi)")
            
        elif faktoriyel_konumu == "Sadece Pay (Üst) Kısmında" or ustel_konumu == "Sadece Pay (Üst) Kısmında":
            st.error("💡 **Tahmini Sonuç:** IRAKSAK")
            st.info("📌 **Açıklama:** Faktöriyel veya üstel ifadenin pay kısmında bulunması, terimlerin hızla büyümesine sebep olur. (Önerilen Test: Oran Testi)")
            
        elif faktoriyel_konumu == "Sadece Payda (Alt) Kısmında" or ustel_konumu == "Sadece Payda (Alt) Kısmında":
            st.success("💡 **Tahmini Sonuç:** YAKINSAK")
            st.info("📌 **Açıklama:** Faktöriyel veya üstel ifadenin paydada bulunması, terimleri çok hızlı bir şekilde sıfıra çeker. (Önerilen Test: Oran Testi)")
            
        else:
            # 3. Aşama: Sadece Polinom Kaldıysa
            st.info("📌 **Önerilen Çözüm Yöntemi:** Limit Karşılaştırma veya p-Serisi Testi")
            if payda_derecesi > pay_derecesi + 1:
                st.success("💡 **Tahmini Sonuç:** YAKINSAK (Paydanın derecesi, paydan en az 2 derece büyük)")
            elif payda_derecesi <= pay_derecesi:
                st.warning("💡 **Tahmini Sonuç:** IRAKSAK (Payın derecesi, paydaya eşit veya daha büyük)")
            else:
                st.warning("💡 **Tahmini Sonuç:** ŞÜPHELİ (Limit sıfıra gidiyor ancak harmonik seri gibi ıraksak olabilir. İntegral Testi gerekebilir.)")
    else:
        st.error("Hata: 'tez veri dosyası.xlsx' dosyası bulunamadı. Lütfen dosyanın yüklü olduğundan emin olun.")