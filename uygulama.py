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















with st.expander("Serinin Davranışını ve Kısmi Toplam Grafiğini İncele"):
    
    # Kullanıcıya daha geniş örnekler sunalım
    formul_girdisi = st.text_input("Grafiği çizilecek genel terim (Örn: 1/(n**2), sin(n)/n, (-1)**n/n):", value="1/(n**2)")
    terim_sayisi = st.slider("Hesaplanacak Terim Sayısı (N)", min_value=10, max_value=500, value=100)
    
    try:
        n_degerleri = np.arange(1, terim_sayisi + 1)
        
        # 1. DÜZELTME: Kullanıcı n^2 yazarsa, Python'ın anladığı n**2 formatına otomatik çevir
        islenmis_formul = formul_girdisi.replace("^", "**")
        
        # 2. DÜZELTME: Python'a matematiksel fonksiyonları öğreten sözlük
        import math
        matematik_sozlugu = {
            "n": n_degerleri,
            "sin": np.sin,
            "cos": np.cos,
            "tan": np.tan,
            "exp": np.exp,
            "log": np.log,    # Doğal logaritma (ln)
            "ln": np.log,     # ln yazılırsa da anlasın
            "sqrt": np.sqrt,
            "pi": np.pi,
            "e": np.e,
            "abs": np.abs,    # Mutlak değer
            "factorial": np.vectorize(math.factorial) # Faktöriyel hesaplaması
        }
        
        # Formülü sadece bizim belirlediğimiz güvenli matematik sözlüğü ile hesapla
        a_n = eval(islenmis_formul, {"__builtins__": None}, matematik_sozlugu)
        
        # Kısmi Toplamları Hesaplama
        S_n = np.cumsum(a_n)
        
        df_grafik = pd.DataFrame({
            "n": n_degerleri,
            "Terimler (a_n)": a_n,
            "Kısmi Toplamlar (S_n)": S_n
        }).set_index("n")
        
        st.markdown("### Kısmi Toplamlar ($S_n$) Grafiği")
        st.info("💡 **Matematiksel Sezgi:** Eğer bu grafik yatay bir çizgiye (asimptota) doğru düzleşiyorsa seri yakınsaktır. Sonsuza doğru tırmanmaya devam ediyorsa ıraksaktır.")
        st.line_chart(df_grafik["Kısmi Toplamlar (S_n)"])
        
        st.markdown("### Dizinin Genel Terimi ($a_n$) Grafiği")
        st.info("💡 **Yakınsaklık Şartı:** Serinin yakınsak olma ihtimali için bu grafiğin $n$ büyüdükçe 0'a gitmesi gerekir.")
        st.line_chart(df_grafik["Terimler (a_n)"])
        
    except Exception as e:
        # 3. DÜZELTME: Hata durumunda kullanıcıya neyi yanlış yazdığını gösterelim
        st.warning(f"Grafik çizilemedi. Lütfen geçerli bir matematiksel ifade girdiğinizden emin olun. (Detay: {e})")









