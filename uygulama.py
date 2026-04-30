import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier

# 1. Sayfa Ayarları
st.set_page_config(page_title="Seri Analizi Yapay Zekası", page_icon="🤖", layout="wide")

# 2. Modeli Eğitme (Uygulama her açıldığında modeli hızlıca hafızaya alır)
@st.cache_resource
def modeli_hazirla():
    # Veriyi Oku
    df = pd.read_excel('tez veri dosyası.xlsx')
    
    # Veriyi Temizle
    df.rename(columns={'Uygun?Test': 'Uygun_Test'}, inplace=True)
    df['Payda_Derecesi'] = df['Payda_Derecesi'].astype(str).str.rstrip('.').astype(float)
    df['Uygun_Test'] = df['Uygun_Test'].astype(str).str.strip()
    df['Uygun_Test'] = df['Uygun_Test'].replace('Karşılaştırm Testi', 'Karşılaştırma Testi')
    df['Uygun_Test'] = df['Uygun_Test'].replace('p-seri testi', 'p-serisi Testi')
    df['Uygun_Test'] = df['Uygun_Test'].replace('nan', np.nan)
    df = df.dropna(subset=['Uygun_Test', 'Karakter_Sonucu'])
    df['Karakter_Sonucu'] = df['Karakter_Sonucu'].astype(int)

    X = df[['Pay_Derecesi', 'Payda_Derecesi', 'Faktöriyel_Var_Mi', 'Ustel_Var_Mi', 
            'n_Uzeri_n_Var_Mi', 'Logaritma_Var_Mi', 'Alterne_Isaret_Var_Mi', 'Trigonometri_Var_Mi']]
    X = X.apply(pd.to_numeric, errors='coerce').fillna(0)

    y_test_adi = df['Uygun_Test']
    y_karakter = df['Karakter_Sonucu']

    # Final sürümü olduğu için verinin %100'ü ile eğitiyoruz ki en zeki haline ulaşsın!
    m_test = RandomForestClassifier(n_estimators=100, random_state=42)
    m_karakter = RandomForestClassifier(n_estimators=100, random_state=42)
    m_test.fit(X, y_test_adi)
    m_karakter.fit(X, y_karakter)
    
    return m_test, m_karakter, X.columns

# Beyinleri yükle
model_test, model_karakter, sutunlar = modeli_hazirla()

# 3. KULLANICI ARAYÜZÜ (Görsel Kısım)
st.title("🤖 Sonsuz Seriler İçin Yapay Zeka Uzmanı")
st.markdown("Bu program, verilen bir matematiksel serinin karakterini ve çözüm yöntemini analiz etmek için **Çift Uzmanlı Random Forest Algoritması** kullanır.")
st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("📝 Serinin Özelliklerini Girin")
    pay_derecesi = st.number_input("Payın Polinom Derecesi", min_value=0.0, step=0.5, value=0.0)
    payda_derecesi = st.number_input("Paydanın Polinom Derecesi", min_value=0.0, step=0.5, value=0.0)
    
    st.markdown("**Formül İçindeki Yapılar:**")
    fak = st.checkbox("Faktöriyel (!) Var Mı?")
    ust = st.checkbox("Üstel İfade (e^n, 2^n vb.) Var Mı?")
    nn = st.checkbox("n^n Yapısı Var Mı?")
    log = st.checkbox("Logaritma (ln, log) Var Mı?")
    alt = st.checkbox("Alterne İşaret (-1)^n Var Mı?")
    trig = st.checkbox("Trigonometrik Fonksiyon (sin, cos) Var Mı?")

with col2:
    st.subheader("🧠 Yapay Zeka Kararı")
    
    # Kullanıcı özelliklerini makinenin anlayacağı veri setine çevir
    kullanici_verisi = pd.DataFrame([[
        pay_derecesi, payda_derecesi, int(fak), int(ust), int(nn), int(log), int(alt), int(trig)
    ]], columns=sutunlar)

    if st.button("Analiz Et", type="primary", use_container_width=True):
        with st.spinner('Yapay zeka hesaplama yapıyor...'):
            tahmin_test = model_test.predict(kullanici_verisi)[0]
            tahmin_karakter = model_karakter.predict(kullanici_verisi)[0]
            
            st.success("Analiz Tamamlandı!")
            
            st.markdown("### 📌 Önerilen Çözüm Yolu:")
            st.info(f"**{tahmin_test}**")
            
            st.markdown("### 🎯 Serinin Karakteri:")
            if tahmin_karakter == 1:
                st.success("🟢 **YAKINSAK**")
            else:
                st.error("🔴 **IRAKSAK**")