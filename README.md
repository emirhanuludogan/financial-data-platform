# Financial Data Platform — EVDS ve PySpark ile Döviz Verisi İşleme

TCMB EVDS'den döviz verisi alan, PySpark ile temizleyen ve önceki gözleme göre
kur değişimini hesaplayan modüler bir veri mühendisliği projesi.

Çalışma; veri alımı, dönüşüm, özellik üretimi ve günlük kaydını Raw/Bronze,
Silver ve Gold katmanlarında bir araya getirir. Mevcut örnek, tek bir seri
ve sabit tarih aralığı üzerinde çalışan **batch ETL** akışıdır.

## Proje ne yapıyor?

1. EVDS'den `TP.DK.USD.S.YTL` serisini **01-01-2024 → 01-01-2026** aralığında çeker.
2. Ham tabloyu `data/raw/` altında Parquet olarak yazar.
3. Tarih ve kur alanlarını dönüştürüp Silver katmanını oluşturur.
4. Tarih sırasındaki önceki değeri ve yüzde değişimi hesaplar.
5. Gold çıktısını Parquet olarak, çalışma günlüklerini `logs/` altında kaydeder.

**EVDS → Raw/Bronze → Silver → Gold**

Bu repo bir öğrenme ve geliştirme çalışmasıdır. Gerçek zamanlı veri akışı,
artımlı yükleme veya üretim ortamı için doğrulanmış bir platform olarak sunulmaz.

## Hızlı başlangıç

Python ve seçtiğiniz PySpark sürümüyle uyumlu bir Java kurulumu gerekir.
`requirements.txt` sürümleri kilitlemez; ortam ayrıntıları
[çalıştırma rehberinde](docs/OPERATIONS.md) açıklanır.

Windows PowerShell:

```powershell
git clone https://github.com/emirhanuludogan/financial-data-platform.git
cd financial-data-platform
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

`.env` dosyasındaki `EVDS_API_KEY` alanına kendi EVDS anahtarınızı yazın.
Ardından repo kökünden çalıştırın:

```powershell
.\.venv\Scripts\python.exe -m src.pipelines.main
```

Windows betiği aynı giriş noktasını çağırır:

```powershell
.\run_pipeline.bat
```

Betik zamanlama oluşturmaz; varsa `.venv` ortamını kullanır ve gerçek çıkış
kodunu iletir. Linux/macOS'ta sanal ortamın `.venv/bin/python` çalıştırıcısıyla
aynı Python modülü çağrılabilir; platform uyumluluğu ayrıca doğrulanmalıdır.

## Çıktılar

| Konum | İçerik |
| --- | --- |
| `data/raw/usd_kur_raw.parquet/` | EVDS'den alınan ham tablonun Spark çıktısı |
| `data/silver/usd_kur_cleaned.parquet/` | `Date`, `USD_Satis` |
| `data/gold/usd_kur_features.parquet/` | Silver alanları, `Prev_USD_Satis`, `Daily_Change_Pct` |
| `logs/pipeline.log` | Katman ve orkestratör günlükleri |
| `logs/automation.log` | Windows betiğinin standart çıktı/hata kaydı |

`.parquet` yolları Spark çıktı dizinleridir. Her koşu mevcut hedefleri yeniler;
Raw dahil katmanlar sürümlü/değişmez arşiv olarak saklanmaz.
Veriler, günlükler ve `.env` yerel tutulur.

## Dönüşüm ve hesaplama

Silver katmanı ham kur alanındaki null kayıtları eler, tarihi `dd-MM-yyyy`
biçiminden date'e ve kur değerini double'a çevirir.

Gold katmanında yüzde değişim:

```text
((mevcut_kur - onceki_gozlem) / onceki_gozlem) * 100
```

Sonuç iki ondalığa yuvarlanır. “Önceki gözlem” önceki takvim günü olmak
zorunda değildir. İlk satırdaki eksik önceki değer/değişim mevcut kodda 0 ile
doldurulur. Şemalar ve veri kalitesi sınırları [mimari notunda](docs/ARCHITECTURE.md)
açıklanır.

## Dosya rehberi

| Yol | Görevi |
| --- | --- |
| [src/pipelines/main.py](src/pipelines/main.py) | Üç katmanı sırayla çağırma, süre ve hata yönetimi |
| [src/ingestion/ingestion.py](src/ingestion/ingestion.py) | EVDS bağlantısı ve Raw yazımı |
| [src/processing.py](src/processing.py) | Silver dönüşümleri |
| [src/features.py](src/features.py) | Önceki gözlem ve değişim hesabı |
| [src/utils.py](src/utils.py) | Ana akışın kullandığı logger ve yardımcılar |
| [notebooks/demo.ipynb](notebooks/demo.ipynb) | Ayrı keşif örneği; CSV ve Parquet çıktısı |
| [run_pipeline.bat](run_pipeline.bat) | Windows'ta modülü çağıran betik |
| [tests/test_pipeline_failures.py](tests/test_pipeline_failures.py) | Hata ve yol çözümü regresyon kontrolleri |

Notebook, Ocak 2024 verisini kullanır ve değişimi dört ondalığa yuvarlar.
Ana pipeline'ın çıktısıyla aynı deney değildir. Notebook'u `notebooks/`
dizininden açın; API anahtarı repo kökündeki `.env` dosyasından okunur.

## Doğrulama ve geliştirme alanları

```powershell
python -m unittest discover -s tests -v
```

Testler ağ/JVM kullanmadan hata akışını denetler. Canlı EVDS ve gerçek Spark
koşusu için API erişimi ve uyumlu ortam gerekir.

Sıradaki alanlar: yapılandırılabilir seri/tarih, daha kapsamlı veri kalitesi
kontrolleri, sürümlü/atomik yazım, gerçek Spark dönüşüm testleri ve ortam sürüm kilidi.

## Kaynaklar ve teşekkür

- [TCMB EVDS](https://evds2.tcmb.gov.tr/)
- [Apache Spark / PySpark kurulumu](https://spark.apache.org/docs/latest/api/python/getting_started/install.html)
- [Veri mimarisi ve notebook farkları](docs/ARCHITECTURE.md)
- [Çalıştırma ve sorun giderme](docs/OPERATIONS.md)

Teknik istişareleri ve desteği için **Onur Güner**'e teşekkürler.
