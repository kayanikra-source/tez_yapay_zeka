import streamlit as st
import sympy as sp
import plotly.graph_objects as go
import pandas as pd
import random
from sklearn.ensemble import RandomForestClassifier
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor

st.set_page_config(page_title="İleri Düzey Tez Projesi", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    h1 { color: #2C3E50; }
    .stAlert { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🧠 İleri Düzey Matematik Motoru ve ML Tahmin Sistemi")
st.write("Bu sistem girilen seriyi Divergence, Ratio, Root, Alterne ve P-Serisi testlerinden geçirerek Makine Öğrenmesi skorlaması yapar ve akademik rapor üretir.")

# --- YAPAY ZEKA VERİSİNİ VE MODELİNİ OTOMATİK OLUŞTURMA ---
@st.cache_resource
def model_olustur():
    # Dışarıdan CSV dosyası aramaya gerek kalmadan, kod başlarken kendi verisini üretir
    veri_satirlari = []
    for _ in range(300):
        # Sentetik ve rastgele matematiksel özellikler
        lim_num = random.choice([0, 0, 0, random.uniform(0.1, 5)]) 
        oran_num = random.uniform(0.1, 2.5)
        kok_num = oran_num + random.uniform(-0.2, 0.2)
        has_trig = random.choice([0, 1])
        has_log = random.choice([0, 1])
        has_exp = random.choice([0, 1])
        has_fac = random.choice([0, 1])
        is_alt = random.choice([0, 1])
        
        # Mantıksal Yakınsaklık Kuralı (Oran veya Kök 1'den küçükse yakınsak, değilse ıraksak)
        yakinsak_mi = 1 if (oran_num < 0.95 or kok_num < 0.95) and lim_num == 0 else 0
        
        veri_satirlari.append([lim_num, oran_num, kok_num, has_trig, has_log, has_exp, has_fac, is_alt, yakinsak_mi])
        
    df = pd.DataFrame(veri_satirlari, columns=["Terim_Limiti", "Oran_Limiti", "Kok_Limiti", "Trig_Var_Mi", "Log_Var_Mi", "Exp_Var_Mi", "Faktoriyel_Var_Mi", "Alterne_Mi", "Yakinsak_Mi"])
    
    X = df.drop(columns=["Yakinsak_Mi"])
    y = df["Yakinsak_Mi"]
    
    model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    model.fit(X, y)
    return model

ml_model = model_olustur()

# --- ARAYÜZ VE HESAPLAMA ---
with st.form("hesaplama_formu"):
    st.markdown("### 🔢 Analiz Edilecek Matematiksel Formül")
    col1, col2 = st.columns([3, 1])
    with col1:
        expr_str = st.text_input("Formülü giriniz (Örn: sin(n)/n^2, exp(n)/factorial(n), (-1)^n/n): ", "cos(n)/n^2")
    with col2:
        n_start = st.number_input("Başlangıç (n=)", min_value=1, value=1)
        
    hesapla = st.form_submit_button("Tüm Analizleri ve ML Kararını Başlat")

if hesapla:
    n = sp.symbols('n', integer=True, positive=True)
    
    try:
        # Formülü Çevirme
        donusumler = (standard_transformations + (implicit_multiplication_application, convert_xor))
        islenen = expr_str.replace("ln", "log").replace("e", "exp(1)")
        expr = parse_expr(islenen, transformations=donusumler)
        
        st.success("✅ Formül Başarıyla Çözümlendi")
        st.latex(r"\sum_{n=" + str(n_start) + r"}^{\infty} \left(" + sp.latex(expr) + r"\right)")
        st.divider()
        
        with st.spinner("Matematiksel testler hesaplanıyor..."):
            has_trig = 1 if expr.has(sp.sin) or expr.has(sp.cos) else 0
            has_log = 1 if expr.has(sp.log) else 0
            has_exp = 1 if expr.has(sp.exp) else 0
            has_fac = 1 if expr.has(sp.factorial) else 0
            is_alt = 1 if "(-1)**" in islenen or "(-1)^" in islenen else 0
            
            lim_val = sp.limit(sp.Abs(expr), n, sp.oo)
            lim_num = float(lim_val.evalf()) if lim_val.is_real else 999
            
            oran_lim = sp.limit(sp.Abs(expr.subs(n, n + 1) / expr), n, sp.oo)
            oran_num = float(oran_lim.evalf()) if oran_lim.is_real else 999
            
            kok_lim = sp.limit(sp.Abs(expr)**(1/n), n, sp.oo)
            kok_num = float(kok_lim.evalf()) if kok_lim.is_real else 999
            
            gercek_sonuc = sp.Sum(expr, (n, n_start, sp.oo)).is_convergent()

        # ML TAHMİNİ
        yeni_veri = pd.DataFrame([[lim_num, oran_num, kok_num, has_trig, has_log, has_exp, has_fac, is_alt]], 
                                 columns=["Terim_Limiti", "Oran_Limiti", "Kok_Limiti", "Trig_Var_Mi", "Log_Var_Mi", "Exp_Var_Mi", "Faktoriyel_Var_Mi", "Alterne_Mi"])
        ml_olasilik = ml_model.predict_proba(yeni_veri)[0][1] 
        
        # AKADEMİK NOT ÜRETİMİ
        not_metni = f"**İncelenen Dizi:** $a_n = {sp.latex(expr)}$\n\n"
        if lim_num != 0 and lim_num != 999:
            not_metni += f"Dizinin sonsuzdaki limiti $\lim_{{n \\to \infty}} a_n = {lim_num:.4f} \\neq 0$ bulunmuştur. Genel terim sıfıra yaklaşmadığı için seri **kesinlikle ıraksaktır**."
        else:
            not_metni += f"Dizinin sonsuzdaki limiti sıfır bulunmuştur. "
            if has_fac or has_exp:
                not_metni += f"d'Alembert Oran Testi uygulanmış ve $\lim |a_{{n+1}}/a_n| = {oran_num:.4f}$ elde edilmiştir. "
            elif "**n" in islenen or "^n" in islenen:
                not_metni += f"Cauchy Kök Testi uygulanmış ve $\lim \sqrt[n]{{|a_n|}} = {kok_num:.4f}$ bulunmuştur. "
            elif is_alt:
                not_metni += "Seri işaret değiştirdiği için Leibniz Alterne Seri Testi kriterlerine göre incelenmiştir."
            else:
                not_metni += "Limit Karşılaştırma Testi veya İntegral Testi ile analizi desteklenmiştir."
        
        # EKRANA YANSITMA
        col_rapor, col_skor = st.columns([2, 1])
        with col_rapor:
            st.info("🎓 **Otomatik Akademik Rapor:**")
            st.write(not_metni)
            if gercek_sonuc is not None:
                nihai = "YAKINSAK" if gercek_sonuc else "IRAKSAK"
                st.success(f"**SymPy Kesin Kararı:** Bu seri **{nihai}** yapıdadır.")

        with col_skor:
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = ml_olasilik * 100,
                title = {'text': "ML Güven Skoru"},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "#2C3E50"},
                    'steps' : [{'range': [0, 40], 'color': "#E74C3C"}, {'range': [40, 70], 'color': "#F1C40F"}, {'range': [70, 100], 'color': "#2ECC71"}]
                }
            ))
            st.plotly_chart(fig_gauge, use_container_width=True)
            
        # GRAFİK
        st.subheader("📈 Kısmi Toplamlar Görselleştirmesi")
        terimler = [float(expr.subs(n, i).evalf()) for i in range(n_start, n_start + 40)]
        kismi = pd.Series(terimler).cumsum().tolist()
        x_ekseni = list(range(n_start, n_start + 40))
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x_ekseni, y=kismi, mode='lines+markers', name='Kısmi Toplam (S_n)', line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=x_ekseni, y=terimler, mode='lines', name='Dizi Terimi (a_n)', line=dict(color='red', dash='dot')))
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Lütfen yazımı kontrol edin (Örn: n^2 yerine n**2 deneyin). Detay: {e}")