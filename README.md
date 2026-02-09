# Financial Data Platform (Spark ETL Pipeline)

Bu proje, TCMB (EVDS) üzerinden alınan finansal verilerin **PySpark** kullanılarak işlendiği, temizlendiği ve analize hazır hale getirildiği uçtan uca bir **Veri Mühendisliği (ETL)** pipeline çalışmasıdır.
Proje, kurumsal standartlara uygun olarak Medallion Architecture (Bronze, Silver, Gold) prensipleriyle yapılandırılmıştır.

---

## Öne Çıkan Özellikler

* **Dinamik Veri Alımı:** TCMB EVDS API entegrasyonu ile gerçek zamanlıya yakın veri çekimi.
* **Büyük Veri İşleme:** PySpark kullanarak verinin dağıtık mimaride işlenmesi.
* **Feature Engineering:** `Window Functions` ve `Lag` metotları kullanılarak günlük döviz kuru değişim yüzdelerinin hesaplanması.
* **Gözlemlenebilirlik (Observability):** Merkezi logging sistemi ile tüm pipeline adımlarının ve çalışma sürelerinin (**runtime**) anlık takibi.
* **Veri Kalitesi (Data Quality):** Eksik verilerin (Null/NaN) temizlenmesi ve şema (schema) doğrulama süreçleri.
* **Kurşun Geçirmez Dosya Yönetimi:** Windows işletim sistemindeki dosya kilitlenme sorunlarını aşmak için shutil kütüphanesi ile hibrit temizlik stratejisi.
* **Cross-Platform Path Yönetimi:** Pathlib kullanılarak Windows/Linux bağımsız dinamik kök dizin (root) tespiti.
* **Çoklu Depolama:** Verilerin hem insan-okunabilir (**CSV**) hem de performans odaklı (**Parquet**) formatlarda kaydedilmesi.
* **Modüler:** Script Yapısı: Her ETL adımının (**Ingestion, Processing, Features**) ayrı ve tek sorumluluğa sahip scriptler tarafından yönetilmesi.
* **Orkestrasyon:** Tüm sürecin merkezi bir main.py üzerinden yönetilmesi.
* **Otomasyon Desteği:** Pipeline'ın her sabah otomatik çalışmasını sağlayan .bat orkestrasyon desteği.

---
##  Veri Mimarisi (Medallion Architecture)

Proje akışı, veriyi ham halinden analitik değere dönüştürmek için şu mantıksal hattı takip eder:

 Raw (Bronze): EVDS API üzerinden çekilen ham verilerin hiçbir değişiklik yapılmadan Parquet formatında saklandığı, "değişmez" (**immutable**) katman.

Silver (Processed): Veri tiplerinin düzenlendiği, eksik verilerin temizlendiği ve verinin analize uygun hale getirildiği "temiz" katman.

Gold (Analytics): İş mantığı (**Business Logic**) eklenerek finansal özelliklerin hesaplandığı, nihai raporlama katmanı.

---

##  Teknoloji Stack'i

* **Dil:** Python 3.10.11
* **Framework:** Apache Spark 
* **Kütüphaneler:**  Python-dotenv, evds, Pathlib, Shutil, Logging
* **Veri Kaynağı:** TCMB EVDS API
* **Depolama:** Parquet, CSV

---

##  Proje Yapısı

├── data/               # Git-ignored: Yerel veri depolama (Raw, Silver, Gold)
│   ├── raw/            # Ham verilerin saklandığı katman (Bronze)
│   ├── silver/         # Temizlenmiş verilerin saklandığı katman
│   └── gold/           # Analiz ve rapor hazır verilerin saklandığı katman
├── logs/               # Git-ignored: Zaman mühürlü pipeline günlükleri
│   └── automation.log  # Merkezi log dosyası (Tüm ETL adımları burada tutulur)
├── notebooks/          # Veri keşfi ve demo görselleştirmeler
├── src/                # ETL Pipeline modülleri
│   ├── ingestion/      # Veri alımı (Raw Layer)
│   │   └── ingestion.py
│   ├── processing.py   # Veri temizleme (Silver Layer)
│   ├── features.py     # Özellik mühendisliği (Gold Layer)
│   └── utils.py        # Merkezi logger ve Spark konfigürasyonu
├── .env                # Git-ignored: API Key yönetimi
├── .gitignore          # Gereksiz dosyaların takibini engelleyen liste
├── main.py             # Pipeline Orkestrasyon (Şef) Scripti
├──  run_pipeline.bat   # Windows Otomasyon Tetikleyicisi (Tek tıkla tüm akışı başlatır)
└── requirements.txt    #  Proje bağımlılıkları (pyspark, pathlib, shutil, python-dotenv eklendi)
------------------------------------------------------------------------------------------------------
 Kurulum ve Çalıştırma

Projeyi yerel ortamınızda çalıştırmak için aşağıdaki adımları sırasıyla takip edin.

1️⃣ Depoyu Klonlayın

Terminalinizi açın ve projeyi bilgisayarınıza indirin:

git clone https://github.com/emirhanuludogan/financial-data-platform.git
cd financial-data-platform

------------------------------------------------------------------------------------------------------

2️⃣ Gerekli Kütüphaneleri Yükleyin
Bash
pip install -r requirements.txt

⚠️ Python 3.10+ kullanmanız önerilir.
 
 ------------------------------------------------------------------------------------------------------ 
  
3️⃣ API Yapılandırması 

Projenin kök dizininde .env adlı bir dosya oluşturun ve
TCMB (EVDS) üzerinden aldığınız API anahtarını aşağıdaki formatta ekleyin:

EVDS_API_KEY=buraya_api_anahtarinizi_yazin

🔐 .env dosyası güvenlik sebebiyle .gitignore içinde yer almaktadır.

------------------------------------------------------------------------------------------------------
4️⃣ Pipeline'ı Başlatın

Bash
Tüm süreci merkezi orkestratör üzerinden tetikleyin:
Bash
python main.py

Alternatif olarak analiz sürecini gözlemlemek için notebooks/demo.ipynb dosyasını kullanabilirsiniz.

Alternatif (Windows Otomasyon): Pipeline'ı her sabah otomatik çalıştırmak için run_pipeline.bat dosyasını Windows Görev Zamanlayıcı'ya tanımlayabilirsiniz.

------------------------------------------------------------------------------------------------------

 ## Windows İçin Mühendislik Çözümleri

Windows kısıtlamaları sebebiyle Spark'ın yaşadığı Unable to clear output directory hatası şu yöntemlerle çözülmüştür:

Hybrid Write: Yazma işlemi öncesi shutil.rmtree(path, ignore_errors=True) ile dosya sistemine doğrudan müdahale.

Single Partition (Coalesce): .coalesce(1) kullanılarak yüzlerce küçük .crc dosyasının kilitlenmesi engellenmiş ve raporlama performansı artırılmıştır.
------------------------------------------------------------------------------------------------------

## Kaynakça (References)
Bu projenin mimarisi ve ETL süreçleri aşağıdaki modern metodoloji takip edilerek geliştirilmiştir:

* **Matt Palmer** - *Understanding ETL: Data Pipelines for Modern Data Architectures* (2024, O'Reilly Media, Inc.)

## 🤝 Teşekkür (Acknowledgments)
* Teknik istişareleri ve desteği için **[Onur Güner]**'e teşekkürler.

------------------------------------------------------------------------------------------------------
