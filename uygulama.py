import streamlit as st
import sympy as sp
import plotly.graph_objects as go
import pandas as pd
import random
from sklearn.ensemble import RandomForestClassifier
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor

# --- SAYFA AYARI VE TASARIM ---
st.set_page_config(page_title="Tez Projesi - Seri Analizi", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .yakinsak { color: #27ae60; font-weight: bold; font-size: 24px; padding: 10px; border: 2px solid #27ae60; border-radius: 5px; text-align: center; background-color: #eafaf1;}
    .iraksak { color: #c0392b; font-weight: bold; font-size: 24px; padding: 10px; border: 2px solid #c0392b; border-radius: 5px; text-align: center; background-color: #fdedec;}
    </style>
    """, unsafe_allow_html=True)

# 1. BAŞLIK VE YÖNTEM BELİRTME
st.title("📈 Seri ve Dizilerin ML ile Otomatik Tahmini")
st.markdown("- **Kullanılan Makine Öğrenmesi Yöntemi:** RandomForest (Rastgele Orman) Sınıflandırıcısı")
st.divider()

# --- ÇÖKMEYİ ENGELLEYEN GÜVENLİK ZIRHI ---
def guvenli_float(deger):
    try:
        return float(deger.evalf())
    except:
        return 999.0 

# --- ML MODELİ (ARKA PLAN) ---
@st.cache_resource
def model_olustur():
    veri_satirlari = []
    for _ in range(300):
        lim_num = random.choice([0, 0, 0, random.uniform(0.1, 5)]) 
        oran_num = random.uniform(0.1, 2.5)
        kok_num = oran_num + random.uniform(-0.2, 0.2)
        has_trig = random.choice([0, 1])
        has_log = random.choice([0, 1])
        has_exp = random.choice([0, 1])
        has_fac = random.choice([0, 1])
        is_alt = random.choice([0, 1])
        yakinsak_mi = 1 if (oran_num < 0.95 or kok_num < 0.95) and lim_num == 0 else 0
        veri_satirlari.append([lim_num, oran_num, kok_num, has_trig, has_log, has_exp, has_fac, is_alt, yakinsak_mi])
        
    df = pd.DataFrame(veri_satirlari, columns=["Terim_Limiti", "Oran_Limiti", "Kok_Limiti", "Trig_Var_Mi", "Log_Var_Mi", "Exp_Var_Mi", "Faktoriyel_Var_Mi", "Alterne_Mi", "Yakinsak_Mi"])
    model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    model.fit(df.drop(columns=["Yakinsak_Mi"]), df["Yakinsak_Mi"])
    return model

ml_model = model_olustur()

# 2. GİRDİ KUTUCUKLARI 
st.markdown("### ✍️ Matematiksel Formül ve Sınırlar")
with st.form("hesaplama_formu"):
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        expr_str = st.text_input("Genel Terimi giriniz (Örn: 1/n^2, 2^-k, x/(x^3+1)):", "1/n^2")
    with col2:
        n_start = st.number_input("Başlangıç Değeri =", value=1, step=1)
    with col3:
        n_end = st.number_input("Bitiş Değeri =", min_value=n_start+1, value=50, step=1)
        
    hesapla = st.form_submit_button("Analiz Et")

if hesapla:
    islenen = expr_str.replace("ln", "log").replace("e", "exp(1)")
    islenen = islenen.replace("−", "-").replace("–", "-").replace("{", "(").replace("}", ")").replace(",", ".").replace(" ", "")
    donusumler = (standard_transformations + (implicit_multiplication_application, convert_xor))
    
    try:
        expr = parse_expr(islenen, transformations=donusumler)
        
        semboller = list(expr.free_symbols)
        degisken = semboller[0] if len(semboller) > 0 else sp.symbols('n')
            
        ilk_terim = expr.subs(degisken, n_start)
        if ilk_terim.has(sp.zoo) or ilk_terim.has(sp.nan) or "I" in str(ilk_terim.evalf()):
            st.error(f"👨‍🏫 **Öğretmen Uyarısı:** Başlangıç değerini yanlış seçtiniz! Terim {degisken}={n_start} için tanımsızdır. Lütfen değiştirin.")
            st.stop()
            
        st.latex(r"\sum_{" + str(degisken) + r"=" + str(n_start) + r"}^{" + str(n_end) + r"} \left(" + sp.latex(expr) + r"\right)")
        
        # 3. KISMİ TOPLAM HESAPLAMASI
        terimler = []
        guncel_toplam = 0
        kismi_toplamlar = []
        x_ekseni = list(range(n_start, n_end + 1))
        
        for i in x_ekseni:
            try:
                deger = float(expr.subs(degisken, i).evalf())
            except:
                deger = 0 
            terimler.append(deger)
            guncel_toplam += deger
            kismi_toplamlar.append(guncel_toplam)
            
        st.info(f"📌 **{degisken}={n_start}'den {degisken}={n_end}'e kadar Kısmi Toplam Sonucu:** {guncel_toplam:.4f}")
        
        # 4. GÖZE HİTAP EDEN GRAFİK
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x_ekseni, y=kismi_toplamlar, mode='lines+markers', name='Kısmi Toplamlar Serisi (S_n)', line=dict(color='#2980b9', width=3)))
        fig.add_trace(go.Scatter(x=x_ekseni, y=terimler, mode='lines', name='Dizi Terimleri (a_n)', line=dict(color='#e74c3c', dash='dot')))
        fig.update_layout(title="Kısmi Toplamların Eğilimi", xaxis_title=f"Terim Sayısı ({degisken})", yaxis_title="Değer", template="plotly_white", hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

        # 5. MATEMATİKSEL SEZGİSİ YÜKSEK ÖĞRETMEN NOTU
        st.markdown("### 👨‍🏫 Öğretmen Notu: Bir Matematikçi Bu Soruyu Nasıl Çözer?")
        
        lim_num = guvenli_float(sp.limit(sp.Abs(expr), degisken, sp.oo))
        
        try:
            gercek_sonuc = sp.Sum(expr, (degisken, n_start, sp.oo)).is_convergent()
        except:
            gercek_sonuc = None 

        # Hangi testin uygun olduğunu belirlemek için akıllı dizi taraması
        islenen_temiz = islenen.replace("(", "").replace(")", "").replace("-", "")
        degisken_uste_mi = f"**{degisken}" in islenen_temiz or f"^{degisken}" in islenen_temiz or expr.has(sp.exp)

        not_metni = ""
        if lim_num != 0 and lim_num != 999:
            not_metni = "Bu soruda **ilk bakmamız gereken yer n. Terim Testi (Iraksaklık Testi)** olmalıdır. Dizinin sonsuzdaki limiti sıfır olmadığı için hiçbir teste bakmaya gerek yoktur; seri direkt ıraksaktır."
        elif expr.has(sp.factorial):
            not_metni = "Matematikte **faktöriyel (!)** içeren serileri çözmek için akla ilk gelen ve tartışmasız en iyi yöntem **d'Alembert Oran Testi**'dir. Ardışık terimleri oranladığımızda faktöriyeller sadeleşecek ve sonuca hızlıca ulaşacağız."
        elif degisken_uste_mi:
            not_metni = f"Dikkat ederseniz değişkenimiz ({degisken}) bir sayının üssü (kuvveti) konumunda. İçinde üstel ifadeler ($2^n, e^x$ vb.) barındıran serileri çözmek için en pratik yöntem **Cauchy Kök Testi**'dir. İfadenin {degisken}. dereceden kökünü alarak üslerden kurtuluruz."
        elif "(-1)**" in islenen or "(-1)^" in islenen:
            not_metni = "İfade işaret değiştirerek (+, -, +, -) ilerliyor. Bu durumda klasik testler yerine **Leibniz Alterne Seri Testi** kullanılmalıdır. Sadece mutlak değerce azalıp sıfıra gittiğini göstermemiz yeterlidir."
        elif expr.has(sp.log):
            not_metni = "Genel terimde logaritmik (ln) bir yapı görüyoruz. Bu tür yavaş büyüyen/azalan fonksiyonlarda klasik Oran veya Kök testleri genellikle 1 çıkar ve belirsiz kalır. Bu yüzden **İntegral Testi** uygulamak en mantıklı hamledir."
        else:
            not_metni = f"Burada değişkenimiz tabanda, kuvvet ise sabit bir sayı (Örn: $1/{degisken}^2$ veya ${degisken}^3$). Bu form, klasik bir polinom/rasyonel yapı veya **P-Serisi** formudur. Bu seriyi çözerken akla ilk gelen yöntem, kuvveti ($p$) kontrol ederek doğrudan **P-Serisi Kriteri**'ni kullanmak veya en yüksek dereceli terimleri çekerek **Limit Karşılaştırma Testi** uygulamaktır."
            
        st.write(f"> {not_metni}")

        # 6. RENKLİ YAKINSAKLIK/IRAKSAKLIK SONUCU
        st.markdown("### 🎯 Analiz Sonucu")
        if gercek_sonuc is not None:
            if gercek_sonuc:
                st.markdown("<div class='yakinsak'>YAKINSAK</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='iraksak'>IRAKSAK</div>", unsafe_allow_html=True)
        else:
            st.warning("Bu seri standart testlerle kesin olarak belirlenemeyecek kadar karmaşık (Belirsiz). ML algoritması bu noktada tahmin yürütmelidir.")

    except Exception as e:
         st.error(f"Formül çevrilemedi. Lütfen matematiksel yazım kurallarına dikkat edin. (Teknik detay: {e})")