# 📊 TÜBA GEBİP Akademik Performans Keşif Aracı

Bu proje, **TÜBA GEBİP (Üstün Başarılı Genç Bilim İnsanı)** ödülü alan araştırmacıların akademik performanslarını analiz etmek ve görselleştirmek amacıyla geliştirilmiştir.

Uygulama, araştırmacıların **Google Scholar** verilerini temel alarak ödül aldıkları yıl ile güncel performanslarını karşılaştırır ve detaylı bir keşif arayüzü sunar.

🔗 **Canlı Demo:** [Streamlit Uygulaması](https://share.streamlit.io/) *(Kendi linkinizi buraya ekleyebilirsiniz)*

## ✨ Özellikler

*   **📈 İnteraktif Keşif Aracı:** Araştırmacıları atıf sayısı, H-indeksi, yayın sayısı gibi metriklere göre filtreleyin ve görselleştirin.
*   **👤 Araştırmacı Profilleri:** Her bir ödül sahibi için detaylı akademik karne, zaman içindeki yayın/atıf artış grafikleri.
*   **🏆 Ödül Anı Analizi:** Araştırmacının ödülü aldığı yıldaki performansının (o anki durumunun) rekonstrüksiyonu ve bugünkü durumla karşılaştırılması.
*   **📊 Özet İstatistikler:** Alanlara ve kurumlara göre dağılımlar.

## 🛠️ Teknolojiler

*   **Python 3.9+**
*   **[Streamlit](https://streamlit.io/):** Web arayüzü ve dashboard.
*   **[Plotly](https://plotly.com/python/):** İnteraktif grafikler.
*   **Pandas:** Veri manipülasyonu ve analizi.
*   **Google Scholar Data:** Serper.dev API kullanılarak zenginleştirilmiş veri seti.

## 🚀 Kurulum ve Çalıştırma

Projeyi yerel makinenizde çalıştırmak için aşağıdaki adımları izleyin:

1.  **Depoyu klonlayın:**
    ```bash
    git clone https://github.com/kullanici_adiniz/repo_adiniz.git
    cd repo_adiniz
    ```

2.  **Gereksinimleri yükleyin:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Uygulamayı başlatın:**
    ```bash
    streamlit run dashboard.py
    ```

## 📂 Veri Seti

Uygulama, `data/gebip_scholar_final.csv` dosyasını kullanır. Bu veri seti şunları içerir:
*   Araştırmacı Adı ve Kurumu
*   Ödül Yılı ve Alanı
*   Google Scholar Metrikleri (Toplam Atıf, H-İndeksi, i10 vb.)
*   **Hesaplanmış Metrikler:** Ödül Yılındaki Atıf ve Yayın sayıları (yıllık geçmiş verisinden hesaplanmıştır).

## 📝 Lisans

Bu proje açık kaynaklıdır ve eğitim/analiz amaçlı geliştirilmiştir.
