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

def guvenli_limit(ifade, degisken):
    try:
        sonuc = sp.limit(ifade, degisken, sp.oo)
        return float(sonuc.evalf())
    except:
        return 999.0 

# Formülün içindeki n^n veya 2^n yapılarını bulan zeki matematiksel tarayıcılar
def degisken_ussu_degisken_mi(ifade, var):
    for arg in sp.preorder_traversal(ifade):
        if arg.is_Pow and arg.exp.has(var) and arg.base.has(var):
            return True
    return False

def sabit_ussu_degisken_mi(ifade, var):
    for arg in sp.preorder_traversal(ifade):
        if arg.is_Pow and arg.exp.has(var) and not arg.base.has(var):
            return True
    return False

# --- ML MODELİ ---
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
        is_p_series = random.choice([0, 1])
        
        # P-Serisi ise oran testi 1 çıksa bile yakınsaklık kurallarını öğrenmesi için:
        yakinsak_mi = 1 if (oran_num < 0.95 or kok_num < 0.95 or (is_p_series==1 and random.choice([0,1])==1)) and lim_num == 0 else 0
        veri_satirlari.append([lim_num, oran_num, kok_num, has_fac, has_n_n, has_log, is_alt, is_p_series, yakinsak_mi])
        
    df = pd.DataFrame(veri_satirlari, columns=["Terim_Limiti", "Oran_Limiti", "Kok_Limiti", "Faktoriyel", "N_Uzeri_N", "Logaritma", "Alterne", "P_Serisi", "Yakinsak_Mi"])
    model = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
    model.fit(df.drop(columns=["Yakinsak_Mi"]), df["Yakinsak_Mi"])
    return model

ml_model = model_olustur()

# --- ARAYÜZ ---
st.markdown("### ✍️ Matematiksel Formül ve Sınırlar")
with st.form("hesaplama_formu"):
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        expr_str = st.text_input("Genel Terimi giriniz (Örn: 1/n^2, cos(n)/n, (-1)^n/n):", "1/n^2")
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

        # --- YENİ EKLENEN ML TAHMİN MOTORU VE ÖZELLİK ÇIKARIMI ---
        lim_num = guvenli_limit(sp.Abs(expr), degisken)
        oran_num = guvenli_limit(sp.Abs(expr.subs(degisken, degisken + 1) / expr), degisken)
        kok_num = guvenli_limit(sp.Abs(expr)**(1/degisken), degisken)
        
        islenen_str = str(expr).replace(" ", "")
        has_fac_val = 1 if expr.has(sp.factorial) else 0
        has_n_n_val = 1 if degisken_ussu_degisken_mi(expr, degisken) else 0
        has_log_val = 1 if expr.has(sp.log) else 0
        is_alt_val = 1 if "(-1)**" in islenen_str or "(-1)^" in expr_str else 0
        
        is_rat_func = False
        num_deg = 0
        try:
            if expr.is_rational_function(degisken):
                is_rat_func = True
                num, den = sp.fraction(sp.cancel(expr))
                if num.is_polynomial(degisken):
                    num_deg = sp.degree(num, degisken)
        except:
            pass

        is_p_series_val = 1 if (is_rat_func and num_deg == 0) else 0

        yeni_veri = pd.DataFrame([[lim_num, oran_num, kok_num, has_fac_val, has_n_n_val, has_log_val, is_alt_val, is_p_series_val]], columns=["Terim_Limiti", "Oran_Limiti", "Kok_Limiti", "Faktoriyel", "N_Uzeri_N", "Logaritma", "Alterne", "P_Serisi"])
        ml_olasilik = ml_model.predict_proba(yeni_veri)[0][1]
        ml_karari = "YAKINSAK" if ml_olasilik > 0.5 else "IRAKSAK"

        gercek_sonuc, mutlak_sonuc = None, None
        try:
            if not (expr.has(sp.sin) or expr.has(sp.cos) or expr.has(sp.tan) or expr.has(sp.cot)):
                gercek_sonuc = sp.Sum(expr, (degisken, n_start, sp.oo)).is_convergent()
                mutlak_sonuc = sp.Sum(sp.Abs(expr), (degisken, n_start, sp.oo)).is_convergent()
        except:
            pass

        # --- DÜZELTİLMİŞ ÖĞRETMEN NOTU (Tez Odaklı) ---
        st.markdown("### 👨‍🏫 Öğretmen Notu: Bu Soru İçin Hangi Test Uygundur?")
        not_metni = ""
        
        if lim_num != 0 and lim_num != 999 and not (expr.has(sp.sin) or expr.has(sp.cos)):
            not_metni = "**Iraksaklık (n. Terim) Testi:** Yakınsak bir serinin genel teriminin limiti sıfır olmalıdır. Bu serinin limiti sıfır olmadığı için diğer testlere bakmaya gerek yoktur; seri doğrudan **Iraksaktır**."
        elif is_alt_val:
            not_metni = "**Leibniz Testi (Alterne Seriler):** İfadede ardışık işaret değiştiren bir çarpan var. Terimlerin mutlak değerce monoton azalarak sıfıra gittiği gösterilirse **Leibniz Testi** ile yakınsadığı kanıtlanır. Mutlak değerinin yakınsaklığı ayrıca P-serisi veya Limit Karşılaştırma ile incelenmelidir."
        elif has_fac_val:
            not_metni = "**D'alembert Oran Testi:** Genel terimde faktöriyel ($n!$) mevcut. Faktöriyel içeren serilerde ardışık terimlerin oranının limitini ($\lim a_{n+1}/a_n$) inceleyen **Oran Testi** kullanılmalıdır; böylece faktöriyeller sadeleşir."
        elif has_n_n_val:
            not_metni = f"**Cauchy Kök Testi:** Değişken hem tabanda hem de üste (kuvvet) bulunuyor (${degisken}^{degisken}$ gibi). Bu durumda serinin genel teriminin n. dereceden kökünü almak işlemleri basitleştireceğinden **Kök Testi** uygulanmalıdır."
        elif sabit_ussu_degisken_mi(expr, degisken) or expr.has(sp.exp):
            not_metni = f"**Geometrik Seri / Kök Testi:** Değişken sadece üs konumunda (Örn: $2^{degisken}$ veya $e^{degisken}$). Bu yapı **Geometrik Seri** formundadır. Ortak çarpanın mutlak değerce 1'den küçük olup olmadığına veya Kök Testine bakılarak çözülür."
        elif expr.has(sp.log):
            not_metni = "**İntegral Testi:** İfadede logaritma ($\ln$) fonksiyonu var. Türevi alındığında rasyonel bir ifadeye döndüğü ve genelde yavaş büyüyen bir fonksiyon olduğu için **İntegral Testi** en sağlıklı sonucu verir."
        elif expr.has(sp.sin) or expr.has(sp.cos) or expr.has(sp.tan) or expr.has(sp.cot):
            not_metni = "**Sıkıştırma veya Dirichlet Testi:** İfadede trigonometrik fonksiyonlar bulunuyor ve bunlar dalgalanır. Paydadaki polinom kuvvetliyse mutlak değerce sınırlandırılarak **Sıkıştırma Testi**; $\cos(n)/n$ gibi zayıfsa dalgalanmadan dolayı **Dirichlet Testi** kullanılarak koşullu yakınsaklığı incelenir."
        elif is_rat_func:
            if num_deg == 0:
                not_metni = f"**P-Serisi (Harmonik) Testi:** Bu ifade sabit bir sayının değişkenin kuvvetine bölümü şeklinde, yani temel bir $1/{degisken}^p$ (**P-Serisi**) formundadır. Paydadaki $p$ kuvvetinin $1$'den büyük olup olmadığı kontrol edilerek doğrudan çözülür."
            else:
                not_metni = "**Limit Karşılaştırma Testi:** Bu ifade, payı ve paydası değişkene bağlı **Rasyonel** bir yapıdadır (Polinom/Polinom). Pay ve paydadaki en yüksek dereceli terimler çekilerek elde edilen basit bir P-serisi ile Limit Karşılaştırma Testi yapılmalıdır."
        else:
            not_metni = "Bu seri temel kuralların karmaşık bir birleşimini içeriyor. Genel terimin asimptotik davranışına göre uygun bir P-serisi ile Limit Karşılaştırma Testi denenmelidir."

        st.write(f"> {not_metni}")

        # --- AKILLI YAKINSAKLIK SONUCU ---
        st.markdown("### 🎯 Analiz Sonucu")
        if gercek_sonuc is not None:
            if gercek_sonuc == True:
                # Sadece dalgalanma veya eksi işareti varsa Koşullu/Mutlak ayrımı yap
                if is_alt_val == 1 or expr.has(sp.sin) or expr.has(sp.cos):
                    if mutlak_sonuc == True:
                        st.success("✅ **SONUÇ: MUTLAK YAKINSAK** (Hem serinin kendisi hem mutlak değeri yakınsıyor)")
                    else:
                        st.warning("⚠️ **SONUÇ: KOŞULLU YAKINSAK** (Seri yakınsıyor ancak mutlak değeri ıraksıyor. Leibniz/Dirichlet durumu!)")
                else:
                    # Pozitif terimli serilerde (1/n^2 gibi) kafasını karıştırmadan sadece YAKINSAK de:
                    st.success("✅ **SONUÇ: YAKINSAK**")
            else:
                st.error("❌ **SONUÇ: IRAKSAK**")
        else:
            st.warning("⚙️ **Sembolik Çözüm Yetersiz:** Bu seri standart klasik testlerle SymPy tarafından kesin olarak çözülemedi.")
            if ml_karari == "YAKINSAK":
                st.success(f"🤖 **YAPAY ZEKA TAHMİNİ:** Makine Öğrenmesi Modeli bu serinin **%{ml_olasilik*100:.1f}** olasılıkla **YAKINSAK** olduğunu öngörüyor.")
            else:
                st.error(f"🤖 **YAPAY ZEKA TAHMİNİ:** Makine Öğrenmesi Modeli bu serinin **%{(1-ml_olasilik)*100:.1f}** olasılıkla **IRAKSAK** olduğunu öngörüyor.")

    except Exception as e:
         st.error(f"Formül matematik motorunu kilitledi. Lütfen daha sade bir yazım deneyin. Detay: {e}")