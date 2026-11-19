# Veri akışı ve çıktı sözleşmesi

## Kapsam

Pipeline, EVDS'den tek seri ve sabit tarih aralığı için toplu veri çeker:

- Seri: `TP.DK.USD.S.YTL`
- Başlangıç: `01-01-2024`
- Bitiş: `01-01-2026`
- Tanım yeri: [ingestion.py](../src/ingestion/ingestion.py)

Bu aralık her çalıştırmada yeniden sorgulanır. Artımlı yükleme, canlı akış
ve günlük tarih güncellemesi uygulanmaz.

## Katmanlar

| Katman | Dönüşüm | Çıktı |
| --- | --- | --- |
| Raw / Bronze | EVDS'nin döndürdüğü tabloyu Spark DataFrame'e çevirme | `data/raw/usd_kur_raw.parquet/` |
| Silver | Tarihi ayrıştırma, ham kur alanındaki null kayıtları eleme, double dönüşümü | `data/silver/usd_kur_cleaned.parquet/` |
| Gold | Tarihe göre sıralama, önceki gözlemi ve yüzde değişimi hesaplama | `data/gold/usd_kur_features.parquet/` |

Bunlar tek bir dosya adı gibi görünse de Spark'ın Parquet çıktı **dizinleridir**;
içlerinde parça dosyaları ve Spark metaverisi bulunur.

Her koşuda hedef dizinler temizlenip yeniden yazılır. Raw katmanı da bu davranışı
izler; tarihçeli, değişmez bir veri arşivi değildir. Medallion yaklaşımı burada
mantıksal veri katmanlarını ayırmak için kullanılır.

## Silver şeması

| Alan | Tip | Kaynak |
| --- | --- | --- |
| `Date` | date | `Tarih`, `dd-MM-yyyy` biçiminden |
| `USD_Satis` | double | `TP_DK_USD_S_YTL` |

Ham alanın null kontrolü, sayısal dönüşümden önce yapılır.
Bu işlem kapsamlı bir şema veya değer aralığı doğrulaması değildir.

## Gold şeması

Gold, Silver alanlarına şunları ekler:

| Alan | Tip | Anlamı |
| --- | --- | --- |
| `Prev_USD_Satis` | double | Tarih sırasındaki önceki mevcut gözlem |
| `Daily_Change_Pct` | double | Önceki gözleme göre yüzde değişim, iki ondalık |

Hesap:

```text
Daily_Change_Pct = round((USD_Satis - Prev_USD_Satis) / Prev_USD_Satis * 100, 2)
```

Örneğin önceki değer 30, mevcut değer 33 ise sonuç %10'dur.
Bu, formülü açıklayan örnektir; gerçek kur kaydı değildir.

Önceki gözlem, hafta sonu ve tatiller nedeniyle önceki takvim günü olmayabilir.
Mevcut kod `na.fill(0)` uygular; ilk satırdaki önceki değer ve değişim 0 ile
doldurulur. Bu değerler “ölçülen değişim sıfırdı” şeklinde yorumlanmamalıdır.

## Hata ve günlük akışı

Ana giriş noktası [src/pipelines/main.py](../src/pipelines/main.py) dosyasıdır.
Ingestion → Processing → Features sırasıyla çağrılır.

Eksik API anahtarı, boş API cevabı veya eksik ara veri hata üretir; orkestratör
hatayı kaydedip 1 çıkış koduyla durur. Sonraki aşamalar başlatılmaz.

Merkezi günlük çağrıları `src.utils.get_logger` üzerinden konsola ve
`logs/pipeline.log` dosyasına yazılır. `src/logger.py` ayrı bir eski logger
uygulamasıdır; ana akış tarafından kullanılmaz.

## Notebook farkları

[demo.ipynb](../notebooks/demo.ipynb) bağımsız bir keşif örneğidir.
Pipeline ile aynı deney olarak ele alınmamalıdır:

| Ayar | Pipeline | Notebook |
| --- | --- | --- |
| Tarih aralığı | 01-01-2024 → 01-01-2026 | 01-01-2024 → 31-01-2024 |
| Değişim yuvarlama | 2 ondalık | 4 ondalık |
| Çıktı | Parquet | CSV ve Parquet |
| Konum | Repo kökündeki `data/` | Notebook çalışma dizinindeki `output_data/` |

Notebook'u `notebooks/` dizininden çalıştırın; `../.env` repo kökündeki
anahtar dosyasını gösterir. Mevcut notebook çıktıları yeni bir doğrulama koşusu değildir.

## Geliştirme alanları

- Tarih ve seri seçimlerini yapılandırmaya taşımak.
- Değişmez Raw sürümleri ve atomik çıktı değiştirme eklemek.
- Tarih, yinelenen gözlem, sayısal dönüşüm ve sıfır payda kontrolleri eklemek.
- Veri kalitesi kontrollerini ve gerçek Spark dönüşüm testlerini genişletmek.
- Python/PySpark/Java sürümlerini doğrulanmış bir ortam dosyasıyla sabitlemek.

[Kurulum ve sorun giderme](OPERATIONS.md) · [Proje özeti](../README.md)
