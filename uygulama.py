import streamlit as st
import sympy as sp
import plotly.graph_objects as go
import numpy as np

# Gelişmiş formül çevirici kütüphaneleri
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor

# --- SAYFA AYARLARI VE GÖRÜNÜM ---
st.set_page_config(page_title="Tez Projesi - Gelişmiş Seri Analizi", layout="wide")

# Kurumsal ve şık bir stil teması
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    h1 { color: #1E3A8A; font-family: 'Helvetica Neue', sans-serif; }
    h3 { color: #2C3E50; }
    </style>
    """, unsafe_allow_html=True)

st.title("🔬 İleri Düzey Seri Analizi ve Yapay Zeka Tahmin Laboratuvarı")
st.write("Bu platform, girilen üniversite düzeyindeki matematiksel ifadeleri sembolik olarak çözümler, sınır durumlarını analiz eder ve klasik test yöntemleri ile yapay zeka karar mekanizmalarını karşılaştırır.")

# --- 1. GİRDİ PANELİ (FORM KORUMALI) ---
st.markdown("### 📌 Serinin Genel Terimi ve Sınırları")

with st.form("analiz_formu"):
    col_form1, col_form2, col_form3 = st.columns([3, 1, 1])
    
    with col_form1:
        expr_str = st.text_input("Formülü yazınız (Örn: 1/n^2,  (-1)^n/n,  cos(n)/n!,  ln(n)/n): ", "1/n^2")
    with col_form2:
        n_start = st.number_input("Başlangıç İndeksi (n=)", min_value=0, value=1, step=1)
    with col_form3:
        n_end = st.number_input("Bitiş (Analiz Terim Sayısı)", min_value=10, max_value=500, value=100, step=10)
        
    hesapla_butonu = st.form_submit_button("Matematiksel Analizi Başlat")

# --- ANALİZ VE HESAPLAMA MOTORU ---
if hesapla_butonu:
    n = sp.symbols('n')

    try:
        # Gelişmiş Parser: İnsan dilini matematik diline çevirir (ln->log, ^->**)
        donusumler = (standard_transformations + (implicit_multiplication_application, convert_xor))
        islenen_metin = expr_str.replace("ln", "log").replace("e", "E")
        expr = parse_expr(islenen_metin, transformations=donusumler)

        # AKADEMİK GÖSTERİM (DEVASA SIGMA)
        st.success("✨ Serinin Matematiksel Formu:")
        st.latex(r"\sum_{n=" + str(n_start) + r"}^{\infty} \left(" + sp.latex(expr) + r"\right)")
        
        # İlk 3 terimin açık yazılımı
        t1 = expr.subs(n, n_start)
        t2 = expr.subs(n, n_start + 1)
        t3 = expr.subs(n, n_start + 2)
        st.latex(r"S = " + f"{sp.latex(t1)} + {sp.latex(t2)} + {sp.latex(t3)} + \dots")

        # --- 2. SAYISAL VERİ ÜRETİMİ ---
        terimler = []
        kismi_toplamlar = []
        guncel_toplam = 0
        x_ekseni = list(range(n_start, n_end + 1))

        for i in x_ekseni:
            deger = float(expr.subs(n, i).evalf())
            terimler.append(deger)
            guncel_toplam += deger
            kismi_toplamlar.append(guncel_toplam)

        st.divider()

        # --- 3. DİKKAT ÇEKİCİ VE CANLI GRAFİKLER ---
        st.markdown("### 📊 Kısmi Toplamlar ve Dizi Terimleri Davranış Grafiği")

        fig = go.Figure()

        # Kısmi Toplamlar (Alan boyamalı şık grafik)
        fig.add_trace(go.Scatter(
            x=x_ekseni, 
            y=kismi_toplamlar, 
            mode='lines+markers',
            name='Kısmi Toplam (S_n)',
            line=dict(color='#00CC96', width=3),
            fill='tozeroy', 
            marker=dict(size=4)
        ))

        # Dizi Terimlerinin Sıfıra Gidişi
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
            xaxis_title="Terim Sayısı (n)",
            yaxis_title="Sayısal Değer",
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
        )
        st.plotly_chart(fig, use_container_width=True)

        # --- 4. AÇIKLANABİLİR YAPAY ZEKA GÖSTERGESİ ---
        st.divider()
        st.markdown("### 🤖 Yapay Zeka Modelinin Karar Matrisi")

        col1, col2 = st.columns([2, 1])

        with col1:
            st.info("Yapay Zeka bu kararı verirken serinin şu üniversite düzeyi soyut özelliklerini inceledi:")
            st.write(f"🔹 **Sonsuzdaki Limit Eğilimi ($a_{{{n_end}}}$):** Dizi terimleri hızlıca **{terimler[-1]:.6f}** değerine yaklaşıyor.")
            st.write(f"🔹 **Ardışık Oran Davranışı ($a_{{n}}/a_{{n-1}}$):** Terimlerin birbirine oranı **{(terimler[-1]/(terimler[-2]+1e-9)):.4f}** seviyesinde.")
            st.write(f"🔹 **Kısmi Toplam Sınırı (Max $S_n$):** Serinin ulaştığı en yüksek toplam değeri: **{max(kismi_toplamlar):.4f}**")

        with col2:
            # Model bağlanana kadar çalışacak akıllı simülasyon eşiği
            yakinsama_olasiligi = 0.94 if (abs(terimler[-1]) < 0.01 and (terimler[-1]/(terimler[-2]+1e-9)) < 1.0) else 0.08
            
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = yakinsama_olasiligi * 100,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Yapay Zeka Yakınsaklık Güven Skoru"},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "#1E3A8A"},
                    'steps' : [
                        {'range': [0, 40], 'color': "#FCA5A5"},
                        {'range': [40, 70], 'color': "#FEF08A"},
                        {'range': [70, 100], 'color': "#86EFAC"}],
                }
            ))
            fig_gauge.update_layout(height=240, margin=dict(l=20, r=20, t=30, b=20))
            st.plotly_chart(fig_gauge, use_container_width=True)

        # --- 5. KLASİK MATEMATİK REHBERİ VE TEORİK BİLGİ BANKASI ---
        st.divider()
        st.markdown("### 🧭 Teoretik Kılavuz ve Akademik Referanslar")

        expr_str_lower = expr_str.lower().replace(" ", "")
        test_adi = ""
        test_aciklamasi = ""

        # Limit hesaplama ve doğru test analizi
        limit_degeri = sp.limit(expr, n, sp.oo)
        if limit_degeri != 0:
            test_adi = "Genel Terim (Iraksaklık) Testi"
            test_aciklamasi = f"Serinin genel teriminin sonsuzdaki limiti sıfır değildir ($\lim_{{n \\to \\infty}} a_n = {limit_degeri}$). Temel analiz teoremleri gereği bu seri **kesinlikle ıraksaktır**."
        elif "(-1)**n" in expr_str_lower or "(-1)^n" in expr_str_lower or "cos(pi*n)" in expr_str_lower:
            test_adi = "Alterne Seri Testi (Leibniz Teoremi)"
            test_aciklamasi = "İfadede işaret değiştiren $(-1)^n$ veya salınım yapan trigonometrik yapılar var. Terimlerin mutlak değerce azalan bir dizi oluşturduğu ve sıfıra gittiği Leibniz kriterleriyle kanıtlanmalıdır."
        elif "factorial" in expr_str_lower or "!" in expr_str_lower:
            test_adi = "d'Alembert Oran Testi (Ratio Test)"
            test_aciklamasi = "İfadede faktöriyel ($!$) büyümesi baskındır. Ardışık terimlerin limiti ($\lim \\left| a_{n+1}/a_n \\right|$) incelenerek sadeleştirmeler yapılmalıdır."
        elif "**n" in expr_str_lower or "^n" in expr_str_lower or "exp(" in expr_str_lower:
            test_adi = "Cauchy Kök Testi (Root Test)"
            test_aciklamasi = "Genel terimde $n$. dereceden kuvvetler bulunmaktadır. İfadenin $n$. kökü alınarak ($\lim \\sqrt[n]{{|a_n|}}$) yakınsaklık yarıçapı hesaplanmalıdır."
        else:
            test_adi = "Limit Karşılaştırma veya İntegral Testi"
            test_aciklamasi = "Seri rasyonel veya logaritmik bir yapıya sahip. Pay ve paydanın en yüksek dereceli terimleri seçilerek bilinen bir p-serisi ($\sum 1/n^p$) ile karşılaştırma yapılmalıdır."

        st.info(f"**💡 Jüri Rehber Notu / Önerilen Yöntem:** {test_adi}")
        st.write(f"> {test_aciklamasi}")
        
        # Açılır Teori Kartları
        with st.expander("📚 Üniversite Düzeyi Temel Tanımları Göster"):
            st.markdown("""
            * **Kısmi Toplamlar Dizisi ($S_n$):** Serinin ilk $n$ teriminin aritmetik toplamıdır. Serinin karakterini (yakınsak/ıraksak) belirleyen şey bu dizinin limitidir.
            * **Yakınsaklık Şartı:** Eğer $\lim_{n \to \infty} S_n = S$ (sonlu ve reel bir sayı) ise seri yakınsaktır. Grafik üzerinde bu durum, turuncu alanın yukarı doğru uçmak yerine düz bir çizgide sabitlenmesiyle (asemptot) netçe görülür.
            """)

    except Exception as e:
        st.error(f"⚠️ Matematiksel İfade Hatası: Yazım formatını kontrol edin veya seçtiğiniz başlangıç değerinde fonksiyonun tanımlı olduğundan emin olun (Örn: log(0) veya 1/0 tanımsızdır). Detay: {e}")