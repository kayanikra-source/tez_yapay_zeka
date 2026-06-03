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
    """Matematiksel bir limiti veya ifadeyi çökmeksizin sayıya çevirir."""
    try:
        return float(deger.evalf())
    except:
        return 999.0 # Çökmek yerine ML modeline 'limit yok' anlamında yüksek bir sayı yollar

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
        expr_str = st.text_input("Genel Terimi giriniz (İstediğiniz harfi kullanabilirsiniz, Örn: 1/x^2, 2^-k, n/(n+1)):", "2^-n")
    with col2:
        n_start = st.number_input("Başlangıç Değeri =", value=1, step=1)
    with col3:
        n_end = st.number_input("Bitiş Değeri =", min_value=n_start+1, value=50, step=1)
        
    hesapla = st.form_submit_button("Analiz Et")

if hesapla:
    # Kullanıcıdan gelen metni kusursuz matematik diline çeviriyoruz
    islenen = expr_str.replace("ln", "log").replace("e", "exp(1)")
    islenen = islenen.replace("−", "-").replace("–", "-").replace("{", "(").replace("}", ")").replace(",", ".").replace(" ", "")
    donusumler = (standard_transformations + (implicit_multiplication_application, convert_xor))
    
    try:
        expr = parse_expr(islenen, transformations=donusumler)
        
        # --- DİNAMİK DEĞİŞKEN YAKALAYICI (n, x, k ne varsa bulur) ---
        semboller = list(expr.free_symbols)
        if len(semboller) > 0:
            degisken = semboller[0] 
        else:
            degisken = sp.symbols('n') # Eğer formülde harf yoksa (örn: sadece 5 girerse) varsayılan 'n' olsun
            
        # Hata kontrolü: İlk terim tanımsız mı?
        ilk_terim = expr.subs(degisken, n_start)
        if ilk_terim.has(sp.zoo) or ilk_terim.has(sp.nan) or "I" in str(ilk_terim.evalf()):
            st.error(f"👨‍🏫 **Öğretmen Uyarısı:** Başlangıç değerini yanlış seçtiniz! Terim {degisken}={n_start} için tanımsızdır. Lütfen başlangıç değerini değiştirin.")
            st.stop()
            
        st.latex(r"\sum_{" + str(degisken) + r"=" + str(n_start) + r"}^{" + str(n_end) + r"} \left(" + sp.latex(expr) + r"\right)")
        
        # 3. KISMİ TOPLAM HESAPLAMASI (Çökme engelli)
        terimler = []
        guncel_toplam = 0
        kismi_toplamlar = []
        x_ekseni = list(range(n_start, n_end + 1))
        
        for i in x_ekseni:
            try:
                deger = float(expr.subs(degisken, i).evalf())
            except:
                deger = 0 # Beklenmeyen karmaşık bir sayı gelirse grafiği çökertmesin diye atla
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

        # 5. ÖĞRETMEN GÖZÜNDEN TEORİK ANALİZ (Güvenli Limitleme)
        st.markdown("### 👨‍🏫 Öğretmen Notu: Bu Soru Nasıl Çözülür?")
        
        lim_num = guvenli_float(sp.limit(sp.Abs(expr), degisken, sp.oo))
        oran_num = guvenli_float(sp.limit(sp.Abs(expr.subs(degisken, degisken + 1) / expr), degisken, sp.oo))
        kok_num = guvenli_float(sp.limit(sp.Abs(expr)**(1/degisken), degisken, sp.oo))
        
        try:
            gercek_sonuc = sp.Sum(expr, (degisken, n_start, sp.oo)).is_convergent()
        except:
            gercek_sonuc = None # SymPy'ın bile gücünün yetmediği sorularda sistemi çökertmez

        not_metni = ""
        if lim_num != 0 and lim_num != 999:
            not_metni = "Birçok test yöntemi vardır ancak bu soruda **ilk bakmamız gereken yer n. Terim Testi (Iraksaklık Testi)** olmalıdır. Dizinin sonsuzdaki limiti sıfır olmadığı için diğer uzun testlere (Oran, Kök vs.) bakmaya hiç gerek yoktur; seri direkt ıraksaktır."
        elif expr.has(sp.factorial):
            not_metni = "Matematikte **faktöriyel (!)** içeren serileri çözmek için tartışmasız en iyi yol **d'Alembert Oran Testi**'dir. Ardışık terimleri birbirine oranlayarak sonuca en hızlı şekilde ulaşırız."
        elif "**" in islenen or "^" in islenen:
            not_metni = "Terimin tamamında veya büyük bir kısmında **üs (kuvvet)** görüyorsak, en pratik yöntem **Cauchy Kök Testi**'dir. İfadenin kökünü alarak üslerden kurtuluruz."
        elif "(-1)**" in islenen or "(-1)^" in islenen:
            not_metni = "İfade işaret değiştirerek ilerliyor. Bu durumda **Leibniz Alterne Seri Testi** kullanılmalıdır. Terimlerin mutlak değerce azalıp sıfıra gittiğini göstermeliyiz."
        else:
            not_metni = "Bu seri rasyonel veya logaritmik bir yapıya sahip. Bu tip sorularda en çok **Limit Karşılaştırma Testi (P-Serisi ile)** veya fonksiyon sürekli/azalan ise **İntegral Testi** tercih edilir."
            
        st.write(f"> {not_metni}")

        # 6. RENKLİ YAKINSAKLIK/IRAKSAKLIK SONUCU
        st.markdown("### 🎯 Analiz Sonucu")
        if gercek_sonuc is not None:
            if gercek_sonuc:
                st.markdown("<div class='yakinsak'>YAKINSAK</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='iraksak'>IRAKSAK</div>", unsafe_allow_html=True)
        else:
            st.warning("Bu seri standart testlerle kesin olarak belirlenemeyecek kadar karmaşık (Belirsiz). ML algoritması bu noktada devreye girmelidir.")

    except Exception as e:
         st.error(f"Formül çevrilemedi. Lütfen matematiksel yazım kurallarına dikkat edin. (Teknik detay: {e})")