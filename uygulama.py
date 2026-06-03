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
    </style>
    """, unsafe_allow_html=True)

st.title("📈 Seri ve Dizilerin ML ile Otomatik Tahmini")
st.markdown("- **Kullanılan Yöntem:** Nöro-Sembolik Yapay Zeka & RandomForest Sınıflandırıcısı")
st.divider()

def guvenli_float(deger):
    try:
        return float(deger.evalf())
    except:
        return 999.0 

# --- ML MODELİ (TABLOYA GÖRE ZENGİNLEŞTİRİLDİ) ---
@st.cache_resource
def model_olustur():
    veri_satirlari = []
    for _ in range(400):
        lim_num = random.choice([0, 0, 0, random.uniform(0.1, 5)]) 
        oran_num = random.uniform(0.1, 2.5)
        kok_num = oran_num + random.uniform(-0.2, 0.2)
        has_fac = random.choice([0, 1])
        has_n_n = random.choice([0, 1])
        has_log = random.choice([0, 1])
        is_alt = random.choice([0, 1])
        is_rational = random.choice([0, 1])
        
        yakinsak_mi = 1 if (oran_num < 0.95 or kok_num < 0.95) and lim_num == 0 else 0
        veri_satirlari.append([lim_num, oran_num, kok_num, has_fac, has_n_n, has_log, is_alt, is_rational, yakinsak_mi])
        
    df = pd.DataFrame(veri_satirlari, columns=["Terim_Limiti", "Oran_Limiti", "Kok_Limiti", "Faktoriyel_Var_Mi", "N_Uzeri_N_Var_Mi", "Log_Var_Mi", "Alterne_Mi", "Rasyonel_Mi", "Yakinsak_Mi"])
    model = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
    model.fit(df.drop(columns=["Yakinsak_Mi"]), df["Yakinsak_Mi"])
    return model

ml_model = model_olustur()

# --- ARAYÜZ ---
st.markdown("### ✍️ Matematiksel Formül ve Sınırlar")
with st.form("hesaplama_formu"):
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        expr_str = st.text_input("Genel Terimi giriniz (Örn: cos(n)/n, (-1)^n/n, n^n/n!):", "cos(n)/n")
    with col2:
        n_start = st.number_input("Başlangıç Değeri =", value=1, step=1)
    with col3:
        n_end = st.number_input("Bitiş Değeri =", min_value=n_start+1, max_value=1000, value=50, step=10)
        
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
            st.error(f"👨‍🏫 **Uyarısı:** Terim {degisken}={n_start} için tanımsızdır. Lütfen başlangıcı değiştirin.")
            st.stop()
            
        st.latex(r"\sum_{" + str(degisken) + r"=" + str(n_start) + r"}^{" + str(n_end) + r"} \left(" + sp.latex(expr) + r"\right)")
        
        # --- KISMİ TOPLAM HESABI VE GRAFİK ---
        terimler, kismi_toplamlar = [], []
        guncel_toplam = 0
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
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x_ekseni, y=kismi_toplamlar, mode='lines+markers', name='Kısmi Toplamlar (S_n)', line=dict(color='#00d2ff', width=4), fill='tozeroy', fillcolor='rgba(0, 210, 255, 0.15)'))
        fig.add_trace(go.Scatter(x=x_ekseni, y=terimler, mode='lines+markers', name='Dizi Terimleri (a_n)', line=dict(color='#ff512f', width=3, dash='dash'), fill='tozeroy', fillcolor='rgba(255, 81, 47, 0.1)'))
        fig.update_layout(title="Kısmi Toplamların Eğilimi", xaxis_title=f"Terim Sayısı ({degisken})", template="plotly_white", hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

        # --- YENİ EKLENEN ML TAHMİN MOTORU ---
        islenen_str = str(expr).replace(" ", "")
        lim_num = guvenli_float(sp.limit(sp.Abs(expr), degisken, sp.oo))
        oran_num = guvenli_float(sp.limit(sp.Abs(expr.subs(degisken, degisken + 1) / expr), degisken, sp.oo))
        kok_num = guvenli_float(sp.limit(sp.Abs(expr)**(1/degisken), degisken, sp.oo))
        
        has_fac_val = 1 if expr.has(sp.factorial) else 0
        has_n_n_val = 1 if f"{degisken}**{degisken}" in islenen_str else 0
        has_log_val = 1 if expr.has(sp.log) else 0
        is_alt_val = 1 if "(-1)**" in islenen_str or "(-1)^" in expr_str else 0
        is_rat_val = 1 if "/" in islenen_str else 0
        
        yeni_veri = pd.DataFrame([[lim_num, oran_num, kok_num, has_fac_val, has_n_n_val, has_log_val, is_alt_val, is_rat_val]], columns=["Terim_Limiti", "Oran_Limiti", "Kok_Limiti", "Faktoriyel_Var_Mi", "N_Uzeri_N_Var_Mi", "Log_Var_Mi", "Alterne_Mi", "Rasyonel_Mi"])
        ml_olasilik = ml_model.predict_proba(yeni_veri)[0][1]
        ml_karari = "YAKINSAK" if ml_olasilik > 0.5 else "IRAKSAK"

        # --- SEMBOLİK (SYMPY) YAKINSAKLIK KONTROLÜ ---
        try:
            gercek_sonuc = sp.Sum(expr, (degisken, n_start, sp.oo)).is_convergent()
            mutlak_sonuc = sp.Sum(sp.Abs(expr), (degisken, n_start, sp.oo)).is_convergent()
        except:
            gercek_sonuc = None
            mutlak_sonuc = None

        # --- ÖĞRETMEN NOTU (Trigonometri Düzeltildi) ---
        st.markdown("### 👨‍🏫 Öğretmen Notu: Bu Soru İçin Hangi Test Uygundur?")
        
        not_metni = ""
        
        if lim_num != 0 and lim_num != 999 and not (expr.has(sp.sin) or expr.has(sp.cos)):
            not_metni = "**N. Terim Testi:** Serinin genel teriminin limiti sıfır olmadığı için, test tablosuna bakmaya gerek kalmadan seri **Iraksaktır**."
        elif expr.has(sp.sin) or expr.has(sp.cos) or expr.has(sp.tan) or expr.has(sp.cot):
            not_metni = f"İfadede trigonometrik fonksiyonlar ($\sin, \cos$ vb.) bulunuyor. Bu fonksiyonlar $-1$ ile $1$ arasında dalgalanır. Eğer paydada güçlü bir seri varsa ($n^2$ gibi) **Karşılaştırma (Sıkıştırma) Testi** uygulanır. Ancak $\cos({degisken})/{degisken}$ gibi durumlarda seri mutlak yakınsak değildir; dalgalanmadan dolayı **Dirichlet Testi** veya **Abel Testi** kullanılarak koşullu yakınsadığı ispatlanır."
        elif "(-1)**" in islenen_str or "(-1)^" in expr_str:
            not_metni = f"İfadede $(-1)^{degisken}$ bulunuyor. Bu bir **Alterne Seri**'dir. Mutlak yakınsaklık kontrolü yapılmalı, genel terimin azalarak sıfıra gittiği **Leibniz Testi** ile kanıtlanmalıdır."
        elif expr.has(sp.factorial):
            not_metni = "Genel terimde faktöriyel ($n!$) içerdiği için, ilk düşünülmesi gereken yöntem **Oran Testi (d'Alembert)** olmalıdır."
        elif f"{degisken}**{degisken}" in islenen_str or f"{degisken}^{degisken}" in expr_str:
            not_metni = f"Tabanda ve üste aynı değişken var ($n^n$). Bu tip durumlarda serinin $n.$ dereceden kökünü almak işleri çok kolaylaştıracağından **Cauchy Kök Testi** veya Oran Testi uygulanmalıdır."
        elif ("**" in islenen_str and f"**{degisken}" in islenen_str) or ("^" in expr_str and f"^{degisken}" in expr_str):
            not_metni = f"Değişkenimiz üs (kuvvet) konumunda ($a^n$). Bu form, **Geometrik Seri** yapısıdır. Ortak çarpanın ($r$) mutlak değerce 1'den küçük olup olmadığına bakılmalıdır."
        elif expr.has(sp.log):
            not_metni = "İfadede logaritma ($\ln$) fonksiyonu var. Türevi alındığında rasyonel bir ifadeye döndüğü için, bu tip sorularda **İntegral Testi** en sağlıklı sonucu verir."
        elif ("/" in expr_str) and (f"{degisken}*" in islenen_str or "+" in islenen_str) and ("**" not in islenen_str or str(degisken)+"**2" in islenen_str or str(degisken)+"**3" in islenen_str):
            if "1/(" in expr_str and "+" not in expr_str and "-" not in expr_str:
                not_metni = f"Bu formül $1/n^p$ yapısına sahip bir **P-Serisi** formudur. $p$ kuvvetinin 1'den büyük olup olmadığına bakılarak çözülür."
            else:
                not_metni = "Bu ifade polinom bölü polinom şeklinde **Rasyonel bir ifadedir**. En yüksek dereceli terimler çekilerek uygun bir P-serisi ile **Limit Karşılaştırma Testi** yapılmalıdır."
        elif expr_str.count(str(degisken)) > 1 and "-" in expr_str:
            not_metni = "İfade parçalanabilir bir yapıya benziyor. Eğer terimler birbirini götürüyorsa, bu bir **Teleskopik Seri**'dir ve kısmı toplamların limitine doğrudan bakılarak çözülür."
        else:
            not_metni = "Bu seri standart kuralların birleşimini içeriyor. Genel terimin gidişatına göre Oran, Kök veya Limit Karşılaştırma testlerinden biri denenmelidir."

        st.write(f"> {not_metni}")

        # --- YAKINSAKLIK SONUCU VE ML DEVREYE GİRİŞİ ---
        st.markdown("### 🎯 Analiz Sonucu")
        if gercek_sonuc is not None:
            if gercek_sonuc == True and mutlak_sonuc == True:
                st.success("✅ **SONUÇ: MUTLAK YAKINSAK** (Serinin kendisi de, mutlak değeri de yakınsıyor)")
            elif gercek_sonuc == True and mutlak_sonuc == False:
                st.warning("⚠️ **SONUÇ: KOŞULLU YAKINSAK** (Seri yakınsıyor ancak mutlak değeri ıraksıyor. Klasik bir dalgalanma/Leibniz durumu!)")
            else:
                st.error("❌ **SONUÇ: IRAKSAK**")
        else:
            st.warning("⚙️ **Sembolik Çözüm Yetersiz:** Bu seri standart klasik testlerle SymPy tarafından kesin olarak çözülemedi.")
            if ml_karari == "YAKINSAK":
                st.success(f"🤖 **YAPAY ZEKA TAHMİNİ:** Makine Öğrenmesi Modeli, özellik çıkarımlarına (limit, oran) dayanarak bu serinin **%{ml_olasilik*100:.1f}** olasılıkla **YAKINSAK** olduğunu öngörüyor.")
            else:
                st.error(f"🤖 **YAPAY ZEKA TAHMİNİ:** Makine Öğrenmesi Modeli, özellik çıkarımlarına (limit, oran) dayanarak bu serinin **%{(1-ml_olasilik)*100:.1f}** olasılıkla **IRAKSAK** olduğunu öngörüyor.")

    except Exception as e:
         st.error(f"Formül çevrilemedi veya hesaplanırken karmaşık bir asimptota denk gelindi. Matematiksel olarak daha sade bir formül girmeyi deneyin. (Teknik detay: {e})")