# Çalıştırma ve sorun giderme

## Ortam

Python, PySpark'ın çalıştırdığı JVM ve EVDS erişimi birlikte gereklidir.
Kuracağınız PySpark sürümü için Python/Java uyumluluğunu
[Apache Spark kurulum belgesinden](https://spark.apache.org/docs/latest/api/python/getting_started/install.html)
kontrol edin. Güncel belge Python 3.11+ ve Java 17+ gereksinimlerini belirtir;
önceki proje README'sinde Python 3.10.11 kullanıldığı kayıtlıdır.
`requirements.txt` sürümleri kilitlemez.

Temel kontroller:

```powershell
python --version
java -version
```

Java kurulumunun bulunabilmesi için `JAVA_HOME` ve `PATH` ayarlarınızı kontrol
edin. Bu repo üçüncü taraf Windows Hadoop çalıştırılabilir dosyaları dağıtmaz;
Windows dosya sistemi/JVM sorunlarının kurulumunuza göre incelenmesi gerekir.

## API anahtarı

Repo kökünde:

```powershell
Copy-Item .env.example .env
```

`.env` dosyasına kendi anahtarınızı yazın:

```dotenv
EVDS_API_KEY=kendi_evds_anahtariniz
```

Örnek değer gerçek anahtar değildir. Kaynak seri ve hesap erişimi için
[TCMB EVDS](https://evds2.tcmb.gov.tr/) kullanılabilir.
Eksik anahtar artık süreci hata ile durdurur.

## Manuel koşu

Repo kökünden:

```powershell
.\.venv\Scripts\python.exe -m src.pipelines.main
```

Yeniden çalıştırma mevcut `data/raw`, `data/silver` ve `data/gold`
hedeflerini yeniler. Saklamak istediğiniz sonuçları başka bir deney dizininde
koruyun. Pipeline'ı aynı hedefler üzerinde eşzamanlı çalıştırmayın.

## Windows betiği

```powershell
.\run_pipeline.bat
```

Betik kendi klasörüne geçer; varsa `.venv/Scripts/python.exe`, yoksa
`PATH` üzerindeki `python` kullanılır. Gerçek modül giriş noktası çağrılır.
Standart çıktı/hata `logs/automation.log` dosyasına eklenir ve Python'un çıkış
kodu çağırana iletilir.

Bu betik tek başına zamanlama oluşturmaz. Tekrarlı çalıştırma istenirse
Windows Görev Zamanlayıcı'da kullanıcı tarafından ayrıca yapılandırılmalıdır.
Mevcut sabit tarih aralığı her koşuda aynı şekilde sorgulanır.

## Sorun tablosu

| Belirti | Kontrol |
| --- | --- |
| `EVDS_API_KEY bulunamadi` | Repo kökünde `.env`, boş olmayan anahtar |
| `ModuleNotFoundError` | Komutun doğru sanal ortamın Python'u ile çalıştırılması |
| Java gateway/JVM hatası | Java sürümü, `JAVA_HOME`, Python/PySpark uyumluluğu |
| Raw/Silver bulunamadı | Önceki aşamanın günlüğü ve beklenen çıktı dizini |
| Dosya silme/yazma hatası | Açık dosya tutan süreçler, yetkiler, eşzamanlı koşular |
| Notebook farklı sonuç üretiyor | Tarih aralığı, yuvarlama ve çıktı konumu farkları |

Hedefleri önce silen mevcut yazma yöntemi atomik değildir. `coalesce(1)`
küçük örnekte parça sayısını azaltır; dosya kilidi sorunlarını garanti olarak
çözmez ve büyük veri için ölçeklenebilirlik iddiası taşımaz.

## Doğrulama

Dış servis veya Spark kurulumu gerektirmeyen hata akışı testleri:

```powershell
python -m unittest discover -s tests -v
```

Bu testler eksik/boş girdi, klasör adından bağımsız yol çözümü ve orkestratörün
hata çıkışını denetler. EVDS, Spark ve dotenv bağımlılıkları taklit edilir;
testlerin geçmesi canlı API veya gerçek JVM dönüşümünün doğrulandığı anlamına gelmez.

[Veri akışı](ARCHITECTURE.md) · [Proje özeti](../README.md)
