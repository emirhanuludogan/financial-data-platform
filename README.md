# 📈 Financial Data Platform (Spark ETL Pipeline)

Bu proje, TCMB (EVDS) üzerinden alınan finansal verilerin **PySpark** kullanılarak işlendiği, temizlendiği ve analize hazır hale getirildiği uçtan uca bir **Veri Mühendisliği (ETL)** pipeline çalışmasıdır.

---

## 🚀 Öne Çıkan Özellikler

* **Dinamik Veri Alımı:** TCMB EVDS API entegrasyonu ile gerçek zamanlıya yakın veri çekimi.
* **Büyük Veri İşleme:** PySpark kullanarak verinin dağıtık mimaride işlenmesi.
* **Feature Engineering:** `Window Functions` ve `Lag` metotları kullanılarak günlük döviz kuru değişim yüzdelerinin hesaplanması.
* **Veri Kalitesi (Data Quality):** Eksik verilerin (Null/NaN) temizlenmesi ve şema (schema) doğrulama süreçleri.
* **Çoklu Depolama:** Verilerin hem insan-okunabilir (**CSV**) hem de performans odaklı (**Parquet**) formatlarda kaydedilmesi.

---

## 🛠️ Teknoloji Stack'i

* **Dil:** Python 3.10.11
* **Framework:** Apache Spark (PySpark)
* **Kütüphaneler:** Pandas, python-dotenv, evds
* **Veri Kaynağı:** TCMB EVDS API
* **Depolama:** Parquet, CSV

---

## 📂 Proje Yapısı

```plaintext
├── notebooks/          # Veri keşfi ve Spark işlemleri (Jupyter Notebook)
├── src/                # Veri çekme ve yardımcı scriptler
├── output_data/        # İşlenmiş Parquet ve CSV çıktıları (Git-ignored)
└── .env                # API Anahtarları ve hassas veriler (Git-ignored)


------------------------------------------------------------------------------------------------------
⚙️ Kurulum ve Çalıştırma

Projeyi yerel ortamınızda çalıştırmak için aşağıdaki adımları sırasıyla takip edin.

1️⃣ Depoyu Klonlayın

Terminalinizi açın ve projeyi bilgisayarınıza indirin:

git clone https://github.com/emirhanuludogan/financial-data-platform.git
cd financial-data-platform

------------------------------------------------------------------------------------------------------

2️⃣ Gerekli Kütüphaneleri Yükleyin

Spark ve API bağlantısı için gerekli Python bağımlılıklarını kurun:

pip install pyspark python-dotenv evds


⚠️ Python 3.10+ kullanmanız önerilir.
 
 ------------------------------------------------------------------------------------------------------ 
  
3️⃣ API Yapılandırması (Kritik Adım)

Projenin kök dizininde .env adlı bir dosya oluşturun ve
TCMB (EVDS) üzerinden aldığınız API anahtarını aşağıdaki formatta ekleyin:

EVDS_API_KEY=buraya_api_anahtarinizi_yazin



🔐 .env dosyası güvenlik sebebiyle .gitignore içinde yer almaktadır.

------------------------------------------------------------------------------------------------------
4️⃣ Analizi Başlatın

Tüm ETL sürecini gözlemlemek için aşağıdaki notebook dosyasını açın:

notebooks/demo.ipynb


Notebook’u VS Code veya Jupyter Notebook üzerinden açarak
hücreleri sırasıyla çalıştırın.
------------------------------------------------------------------------------------------------------