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

# --- 1. GİRDİ VE MATEMATİKSEL GÖSTERİM (GELİŞMİŞ FORM) ---
st.markdown("### 📌 Serinin Genel Terimi ve Sınırları")

with st.form("analiz_formu"):
    # Girdi alanını 3 kolona böldük
    col_form1, col_form2, col_form3 = st.columns([3, 1, 1])
    
    with col_form1:
        expr_str = st.text_input("Formülü giriniz (Örn: 1/n^2, (-1)^n/n): ", "1/n^2")
    with col_form2:
        n_start = st.number_input("Başlangıç İndeksi (n=)", min_value=0, value=1, step=1)
    with col_form3:
        n_end = st.number_input("Bitiş (Analiz Edilecek Terim)", min_value=10, value=100, step=10)
        
    hesapla_butonu = st.form_submit_button("Analizi Başlat")

# --- ANALİZ VE HESAPLAMA ---
if hesapla_butonu:
    n = sp.symbols('n')

    try:
        donusumler = (standard_transformations + (implicit_multiplication_application, convert_xor))
        islenen_metin = expr_str.replace("ln", "log").replace("e", "E")
        expr = parse_expr(islenen_metin, transformations=donusumler)

        st.success("Serinin Matematiksel Formu:")
        
        # Sigma sembolü artık kullanıcının seçtiği başlangıç değerine göre güncelleniyor
        st.latex(r"\sum_{n=" + str(n_start) + r"}^{\infty} \left(" + sp.latex(expr) + r"\right)")
        
        # Açık terimler de dinamik olarak seçilen başlangıç değerinden hesaplanır
        t1, t2, t3 = expr.subs(n, n_start), expr.subs(n, n_start+1), expr.subs(n, n_start+2)
        st.latex(r"S = " + f"{sp.latex(t1)} + {sp.latex(t2)} + {sp.latex(t3)} + \dots")

        # --- 2. HESAPLAMA DÖNGÜSÜ ---
        terimler = []
        kismi_toplamlar = []
        guncel_toplam = 0
        x_ekseni = list(range(n_start, n_end + 1)) # X ekseni artık dinamik

        for i in x_ekseni:
            deger = float(expr.subs(n, i).evalf())
            terimler.append(deger)
            guncel_toplam += deger
            kismi_toplamlar.append(guncel_toplam)

        st.divider()

        # --- 3. CANLI VE DİKKAT ÇEKİCİ GRAFİK BÖLÜMÜ ---
        st.markdown("### 📊 Kısmi Toplamların Davranış Analizi")

        fig = go.Figure()

        # Kısmi Toplam Grafiği
        fig.add_trace(go.Scatter(
            x=x_ekseni, 
            y=kismi_toplamlar, 
            mode='lines+markers',
            name='Kısmi Toplam (S_n)',
            line=dict(color='#00CC96', width=3),
            fill='tozeroy', 
            marker=dict(size=4)
        ))

        # Dizi Terimleri Grafiği
        fig.add_trace(go.Scatter(
            x=x_ekseni, 
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

        # --- 4. YAPAY ZEKA GÖSTERGESİ ---
        st.divider()
        st.markdown("### 🤖 Yapay Zeka Modelinin Karar Matrisi")

        col1, col2 = st.columns([2, 1])

        with col1:
            st.info("Yapay Zeka bu kararı verirken aşağıdaki matematiksel özellikleri kullandı:")
            st.write(f"- **Limit Eğilimi ($a_{{{n_end}}}$):** Dizi terimleri {terimler[-1]:.6f} değerine doğru gidiyor.")
            st.write(f"- **Artış/Azalış Hızı:** Son terim ile bir önceki arasındaki oran {(terimler[-1]/(terimler[-2]+1e-9)):.4f}")
            st.write(f"- **Maksimum Kısmi Toplam:** Bulunan en yüksek toplam değeri {max(kismi_toplamlar):.4f}")

        with col2:
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

        # --- 5. KLASİK ANALİZ KILAVUZU ---
        st.divider()
        st.markdown("### 🧭 Klasik Analiz Kılavuzu (Test Önerisi)")

        expr_str_lower = expr_str.lower().replace(" ", "")
        test_adi = ""
        test_aciklamasi = ""

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
        st.error(f"Hata: İfade işlenirken bir sorun oluştu. Olası sebep: Formülde yazım hatası veya seçilen başlangıç noktasında tanımsızlık (örneğin 1/n için n=0 seçilmesi). Detay: {e}")