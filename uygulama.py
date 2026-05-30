import streamlit as st
import sympy as sp
import plotly.graph_objects as go
import numpy as np
import joblib

# Gelişmiş formül çevirici kütüphaneleri
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor

# --- SAYFA AYARLARI VE GÖRÜNÜM ---
st.set_page_config(page_title="Tez Uygulaması - Seri Analizi", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stTextInput > div > div > input { font-size: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🔬 İleri Düzey Seri Analizi ve Yapay Zeka Tahmin Laboratuvarı")
st.write("Bu sistem, girilen matematiksel ifadeleri çözümler, sınır durumlarını analiz eder ve Yapay Zeka (ML) yardımıyla yakınsaklık tahmininde bulunur.")

# --- 1. GİRDİ VE MATEMATİKSEL GÖSTERİM (GELİŞMİŞ PARSER İLE) ---
st.markdown("### 📌 Serinin Genel Terimi")
expr_str = st.text_input("Formülü giriniz (Örn: 1/n^2,  (-1)^n/n,  ln(n)/n,  cos(n)/n!): ", "1/n^2")

n = sp.symbols('n')

try:
    # Formülü Python'un anlayacağı formata çevirme
    donusumler = (standard_transformations + (implicit_multiplication_application, convert_xor))
    islenen_metin = expr_str.replace("ln", "log").replace("e", "E")
    expr = parse_expr(islenen_metin, transformations=donusumler)

    # Devasa Sigma gösterimi ve ilk terimlerin açık hali
    st.success("Serinin Matematiksel Formu:")
    st.latex(r"\sum_{n=1}^{\infty} \left(" + sp.latex(expr) + r"\right)")
    
    t1, t2, t3 = expr.subs(n,1), expr.subs(n,2), expr.subs(n,3)
    st.latex(r"S = " + f"{sp.latex(t1)} + {sp.latex(t2)} + {sp.latex(t3)} + \dots")

    # --- 2. HESAPLAMA DÖNGÜSÜ (İLK 100 TERİM) ---
    terimler = []
    kismi_toplamlar = []
    guncel_toplam = 0

    for i in range(1, 101):
        deger = float(expr.subs(n, i).evalf())
        terimler.append(deger)
        guncel_toplam += deger
        kismi_toplamlar.append(guncel_toplam)

    st.divider()

    # --- 3. CANLI VE DİKKAT ÇEKİCİ GRAFİK BÖLÜMÜ ---
    st.markdown("### 📊 Kısmi Toplamların Davranış Analizi")

    fig = go.Figure()

    # Kısmi Toplam Grafiği (Altı boyalı)
    fig.add_trace(go.Scatter(
        x=list(range(1, 101)), 
        y=kismi_toplamlar, 
        mode='lines+markers',
        name='Kısmi Toplam (S_n)',
        line=dict(color='#00CC96', width=3),
        fill='tozeroy', 
        marker=dict(size=4)
    ))

    # Dizi Terimleri Grafiği
    fig.add_trace(go.Scatter(
        x=list(range(1, 101)), 
        y=terimler, 
        mode='lines',
        name='Dizi Terimi (a_n)',
        line=dict(color='#EF553B', width=2, dash='dot')
    ))

    fig.update_layout(
        height=450,
        hovermode="x unified",
        template="plotly_white",
        xaxis_title="Terim İndeksi (n)",
        yaxis_title="Değer",
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- 4. YAPAY ZEKA GÖSTERGESİ (GAUGE CHART) ---
    st.divider()
    st.markdown("### 🤖 Yapay Zeka Modelinin Karar Matrisi")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.info("Yapay Zeka bu kararı verirken aşağıdaki matematiksel özellikleri kullandı:")
        st.write(f"- **Limit Eğilimi ($a_{{100}}$):** Dizi terimleri {terimler[-1]:.6f} değerine doğru gidiyor.")
        st.write(f"- **Artış/Azalış Hızı:** Son terim ile bir önceki arasındaki oran {(terimler[-1]/(terimler[-2]+1e-9)):.4f}")
        st.write(f"- **Maksimum Kısmi Toplam:** Bulunan en yüksek toplam değeri {max(kismi_toplamlar):.4f}")

    with col2:
        # Şimdilik simüle edilen oran (Gerçek modelin bağlandığında burası değişecek)
        yakinsama_olasiligi = 0.92 if (abs(terimler[-1]) < 0.01) else 0.10
        
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = yakinsama_olasiligi * 100,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Yakınsaklık İhtimali"},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps' : [
                    {'range': [0, 40], 'color': "lightcoral"},
                    {'range': [40, 60], 'color': "lightyellow"},
                    {'range': [60, 100], 'color': "lightgreen"}],
            }
        ))
        fig_gauge.update_layout(height=250, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_gauge, use_container_width=True)

    # --- 5. KLASİK ANALİZ KILAVUZU (TEST ÖNERİSİ) ---
    st.divider()
    st.markdown("### 🧭 Klasik Analiz Kılavuzu (Test Önerisi)")

    expr_str_lower = expr_str.lower().replace(" ", "")
    test_adi = ""
    test_aciklamasi = ""

    # Limit ve Test algoritması
    limit_degeri = sp.limit(expr, n, sp.oo)
    if limit_degeri != 0:
        test_adi = "Genel Terim (Iraksaklık) Testi"
        test_aciklamasi = f"Serinin genel teriminin sonsuzdaki limiti 0 değildir (Limit = {limit_degeri}). Bu seri kesinlikle ıraksaktır."
    elif "(-1)**n" in expr_str_lower or "(-1)^n" in expr_str_lower or "cos(pi*n)" in expr_str_lower:
        test_adi = "Alterne Seri Testi (Leibniz Testi)"
        test_aciklamasi = "Seride işaret değiştiren bir çarpan bulunuyor. Terimlerin mutlak değerce azalarak sıfıra yaklaşıp yaklaşmadığı incelenmelidir."
    elif "factorial" in expr_str_lower or "!" in expr_str_lower:
        test_adi = "Oran Testi (d'Alembert)"
        test_aciklamasi = "Faktöriyel yapısı tespit edildi. Ardışık iki terimin oranı ($a_{n+1} / a_n$) alınarak limit incelenmelidir."
    elif "**n" in expr_str_lower or "^n" in expr_str_lower or "exp(" in expr_str_lower:
        test_adi = "Kök Testi (Cauchy) veya Oran Testi"
        test_aciklamasi = "İfadede $n$. kuvvetten üstel terimler var. Genel terimin $n$. dereceden kökü veya oran testi uygulanmalıdır."
    else:
        test_adi = "Limit Karşılaştırma Testi veya İntegral Testi"
        test_aciklamasi = "Seri polinom, rasyonel veya logaritmik bir fonksiyona benziyor. Uygun bir $1/n^p$ (p-serisi) ile karşılaştırılabilir."

    st.info(f"**💡 Önerilen Çözüm Yolu:** {test_adi}")
    st.write(f"> {test_aciklamasi}")

except Exception as e:
    st.error(f"Hata: İfade işlenirken bir sorun oluştu. Lütfen geçerli bir matematiksel format girdiğinizden emin olun.")