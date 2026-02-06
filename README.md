# 📈 Financial Data Platform (Spark ETL Pipeline)

Bu proje, TCMB (EVDS) üzerinden alınan finansal verilerin **PySpark** kullanılarak işlendiği, temizlendiği ve analize hazır hale getirildiği uçtan uca bir **Veri Mühendisliği (ETL)** pipeline çalışmasıdır.
Proje, kurumsal standartlara uygun olarak Medallion Architecture (Bronze, Silver, Gold) prensipleriyle yapılandırılmıştır.

---

## 🚀 Öne Çıkan Özellikler

* **Dinamik Veri Alımı:** TCMB EVDS API entegrasyonu ile gerçek zamanlıya yakın veri çekimi.
* **Büyük Veri İşleme:** PySpark kullanarak verinin dağıtık mimaride işlenmesi.
* **Feature Engineering:** `Window Functions` ve `Lag` metotları kullanılarak günlük döviz kuru değişim yüzdelerinin hesaplanması.
* **Veri Kalitesi (Data Quality):** Eksik verilerin (Null/NaN) temizlenmesi ve şema (schema) doğrulama süreçleri.
* **Çoklu Depolama:** Verilerin hem insan-okunabilir (**CSV**) hem de performans odaklı (**Parquet**) formatlarda kaydedilmesi.
* **Modüler:** Script Yapısı: Her ETL adımının (**Ingestion, Processing, Features**) ayrı ve tek sorumluluğa sahip scriptler tarafından yönetilmesi.
* **Orkestrasyon:** Tüm sürecin merkezi bir main.py üzerinden yönetilmesi.

---
## 🏗️ Veri Mimarisi (Medallion Architecture)

Proje, veriyi ham halinden analitik değere dönüştürmek için üç katmanlı bir hiyerarşi kullanır:

Bronze (Raw): EVDS API üzerinden çekilen ham verilerin hiçbir değişiklik yapılmadan Parquet formatında saklandığı katman.

Silver (Processed): Veri tiplerinin düzenlendiği, eksik verilerin (Null/NaN) temizlendiği ve şema doğrulamasının yapıldığı katman.

Gold (Analytics): Window Functions ve Lag metotları kullanılarak finansal özelliklerin (günlük değişim yüzdeleri vb.) hesaplandığı analitik katman.
---

## 🛠️ Teknoloji Stack'i

* **Dil:** Python 3.10.11
* **Framework:** Apache Spark 
* **Kütüphaneler:**  Python-dotenv, evds
* **Veri Kaynağı:** TCMB EVDS API
* **Depolama:** Parquet, CSV

---

## 📂 Proje Yapısı

├── data/               # Git-ignored (Raw, Silver, Gold katmanları)
├── notebooks/          # Veri keşfi ve demo görselleştirmeler
├── src/                # ETL Pipeline modülleri
│   ├── ingestion/      # Veri alımı (Bronze)
│   ├── processing.py   # Veri temizleme (Silver)
│   ├── features.py     # Özellik mühendisliği (Gold)
│   └── utils.py        # Spark ve Env yardımcı fonksiyonları
├── .env                # API Anahtarları (Git-ignored)
├── .gitignore          # Gereksiz dosyaların takibini engelleyen liste
└── main.py             # Pipeline Orkestrasyon Scripti         # API Anahtarları ve hassas veriler (Git-ignored)


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
4️⃣ Pipeline'ı Başlatın

Tüm ETL sürecini (Ingestion -> Processing -> Features) tek bir komutla çalıştırabilirsiniz:

Bash
python main.py

Alternatif olarak analiz sürecini gözlemlemek için notebooks/demo.ipynb dosyasını kullanabilirsiniz.

------------------------------------------------------------------------------------------------------