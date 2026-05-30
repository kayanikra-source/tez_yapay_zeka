import streamlit as st
import sympy as sp
import numpy as np
import plotly.graph_objects as go
import joblib 

# Gelişmiş matematik formülü okuyucu (Parser) için gereken özel kütüphaneler:
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor
# 1. SAYFA AYARLARI VE GÖRSEL TASARIM
st.set_page_config(page_title="Tez Uygulaması - Seri Analizi", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stTextInput > div > div > input { font-size: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🔢 Dizi ve Serilerin Yakınsaklık Analizi")
st.write("Bu uygulama, matematiksel ifadeleri analiz eder, görselleştirir ve Yapay Zeka (ML) ile tahmin yürütür.")

# --- SİLECEĞİN KISIM BURASIYDI (ESKİ SEÇENEK KUTULARI) ---
# --- EKLEYECEĞİN KISIM BURASI (YENİ FORMÜL GİRİŞİ) ---

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Matematiksel İfade")
    expr_str = st.text_input("Serinin genel terimini girin ($a_n$):", "1/n**2")
    st.info("İpucu: n kare için n**2, n küp için n**3, karekök n için sqrt(n) yazın.")

    # MATEMATİKSEL İŞLEME MOTORU (SymPy)
    n = sp.symbols('n')
    try:
        # 1. Kullanıcı dostu dönüştürücüler (Örn: "^" işaretini üs alma yapar, "2n" yazılırsa "2*n" anlar)
        donusumler = (standard_transformations + (implicit_multiplication_application, convert_xor))
        
        # 2. Özel matematiksel terimleri düzeltme (ln -> log, e -> E)
        islenen_metin = expr_str.replace("ln", "log").replace("e", "E")
        
        # 3. Formülü çözme (Gelişmiş Parser)
        expr = parse_expr(islenen_metin, transformations=donusumler)
        
        st.write("Algılanan Formül:")
        st.latex(f"a_n = {sp.latex(expr)}")
        
        # Sayısal hesaplama (İlk 50 terim)
        terimler = []
        kismi_toplamlar = []
        toplam = 0
        for i in range(1, 51):
            deger = float(expr.subs(n, i).evalf())
            terimler.append(deger)
            toplam += deger
            kismi_toplamlar.append(toplam)
            
    except Exception as e:
        st.error(f"Hata: Yazdığınız ifade tam olarak anlaşılamadı. Lütfen kontrol edin. (Teknik detay: {e})")
        st.stop()

# 2. GÖRSELLEŞTİRME (GRAFİK)
with col2:
    st.subheader("2. Davranış Grafiği")
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=kismi_toplamlar, mode='lines+markers', name='Kısmi Toplamlar (Sn)', line=dict(color='#ff4b4b')))
    fig.add_trace(go.Scatter(y=terimler, mode='lines+markers', name='Terimler (an)', line=dict(color='#0068c9')))
    fig.update_layout(height=400, margin=dict(l=0, r=0, t=30, b=0), legend=dict(orientation="h"))
    st.plotly_chart(fig, use_container_width=True)

# 3. YAPAY ZEKA VE ÖZELLİK ÇIKARIMI (TEZİN CAN DAMARI)
st.divider()
st.subheader("3. Yapay Zeka Tahmin Motoru")

# Yapay zeka senin seçtiğin kutucuklara değil, formülün şu özelliklerine bakacak:
ozellik1 = terimler[0]       # İlk terim
ozellik2 = terimler[-1]      # 50. terim (limit eğilimi)
ozellik3 = terimler[-1] / terimler[-2] if terimler[-2] != 0 else 0 # Oran testi tahmini

c1, c2, c3 = st.columns(3)
c1.metric("İlk Terim Değeri", round(ozellik1, 4))
c2.metric("50. Terim Değeri (L)", round(ozellik2, 4))
c3.metric("Ardışık Oran (an/an-1)", round(ozellik3, 4))

# MODELİ ÇALIŞTIRMA
# Not: Eğer bir .pkl dosyan varsa buraya bağlayacağız. 
# Şimdilik "Yapay Zeka Mantığı"nı buraya kuruyoruz:

if st.button("Yapay Zeka Analizini Başlat"):
    with st.spinner('Model hesaplıyor...'):
        # BURASI TAHMİN KISMI
        # Eğer gerçek bir modelin yoksa şimdilik mantıksal bir AI simülasyonu yapalım:
        if abs(ozellik2) < 0.001 and ozellik3 < 1:
            st.success("🤖 YAPAY ZEKA SONUCU: **YAKINSAK (CONVERGENT)**")
            st.balloons()
        else:
            st.error("🤖 YAPAY ZEKA SONUCU: **IRAKSAK (DIVERGENT)**")

    st.write("---")
    st.write("**Akademik Not:** Model, serinin genel terimini matematiksel olarak çözmez; terimlerin sayısal değişim trendinden (ilk 50 terimdeki azalış hızı ve limit eğilimi) yakınsaklık tahmini yapar.")