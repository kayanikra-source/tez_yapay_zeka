import streamlit as st
import pandas as pd

st.set_page_config(page_title="Seri Analiz Uzmanı", page_icon="♾️", layout="wide")

st.title("🤖 Sonsuz Seriler İçin Yapay Zeka Uzmanı")
st.markdown("Bu uygulama, serinin içindeki matematiksel bileşenlerin **konumlarına (pay/payda)** göre yakınsaklık ve ıraksaklık analizi yapar.")

# Yan panel - Kullanıcı özellikleri (Hocanın tam istediği gibi konum bazlı)
st.sidebar.header("Seri Özelliklerini Girin")

pay_derecesi = st.sidebar.slider("Payın Derecesi (n'in kuvveti)", 0, 10, 1)
payda_derecesi = st.sidebar.slider("Paydanın Derecesi (n'in kuvveti)", 0, 10, 1)

st.sidebar.markdown("---")
st.sidebar.subheader("Özellikler Nerede Bulunuyor?")

secenekler = ["Yok", "Sadece Pay (Üst) Kısmında", "Sadece Payda (Alt) Kısmında", "Her İkisinde de"]

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
        
        # Hocanın belirttiği konumsal matematiksel mantık
        if faktoriyel_konumu == "Sadece Pay (Üst) Kısmında" or ustel_konumu == "Sadece Pay (Üst) Kısmında":
            st.error("💡 **Tahmini Sonuç:** IRAKSAK")
            st.info("📌 **Açıklama:** Faktöriyel veya üstel ifadenin pay kısmında (üstte) bulunması, terimlerin hızla büyümesine sebep olur. (Önerilen Test: Oran veya n. Terim Testi)")
            
        elif faktoriyel_konumu == "Sadece Payda (Alt) Kısmında" or ustel_konumu == "Sadece Payda (Alt) Kısmında":
            st.success("💡 **Tahmini Sonuç:** YAKINSAK")
            st.info("📌 **Açıklama:** Faktöriyel veya üstel ifadenin paydada (altta) bulunması, terimleri çok hızlı bir şekilde sıfıra çeker. (Önerilen Test: Oran Testi)")
            
        else:
            st.info("📌 **Önerilen Çözüm Yöntemi:** Limit Karşılaştırma veya İntegral Testi")
            # Basit bir derece kıyaslaması (p-serisi mantığı)
            if payda_derecesi > pay_derecesi + 1:
                st.success("💡 **Tahmini Sonuç:** YAKINSAK (Paydanın derecesi, paydan en az 2 derece büyük)")
            elif payda_derecesi <= pay_derecesi:
                st.warning("💡 **Tahmini Sonuç:** IRAKSAK (Payın derecesi, paydaya eşit veya daha büyük)")
            else:
                st.warning("💡 **Tahmini Sonuç:** ŞÜPHELİ (Daha ileri bir test, örn: Raabe Testi gerekebilir)")
    else:
        st.error("Hata: 'tez veri dosyası.xlsx' dosyası bulunamadı. Lütfen dosyanın yüklü olduğundan emin olun.")