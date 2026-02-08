import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from evds import evdsAPI
from pyspark.sql import SparkSession
# 1. Merkezi Logger'ı içeri aktarıyoruz
from src.utils import get_logger 

# Logger'ı bu katman özelinde isimlendirerek başlatıyoruz
logger = get_logger("Ingestion_Layer")

# Ortam ve Yol Yapılandırması (Global seviyede bırakılabilir)
root_dir = Path(__file__).resolve().parents[2]
dotenv_path = root_dir / ".env"
load_dotenv(dotenv_path=dotenv_path)

# Windows Spark Ayarları
os.environ['PYSPARK_PYTHON'] = sys.executable
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable

def run_ingestion():
    """
    TCMB EVDS üzerinden veri çekme ve Raw katmanına yazma süreci.
    Prensip: Store first, act later (Ham veriyi koru).
    """
    api_key = os.getenv("EVDS_API_KEY")
    
    # KİTAP PRENSİBİ: Hata durumunda logger.error kullanımı 
    if not api_key:
        logger.error("API ANAHTARI BULUNAMADI! Lutfen .env dosyasini kontrol edin.")
        return

    logger.info(f"ETL Baslatildi --- Root Dizini: {root_dir}")

    try:
        # 2. Veri Çekme Aşaması
        #  Timeliness ve Freshness takibi 
        logger.info("TCMB EVDS API'sine baglanti kuruluyor...")
        evds = evdsAPI(api_key)
        
        # Veri çekme işlemi
        df_pandas = evds.get_data(["TP.DK.USD.S.YTL"], startdate="01-01-2024", enddate="01-01-2026")
        
        #  Veri hacmi (Volume) kontrolü 
        if df_pandas is None or len(df_pandas) == 0:
            logger.warning("API'den bos veri dondu! Ingestion durduruluyor.")
            return
            
        logger.info(f"Veri basariyla cekildi. Kayit Sayisi: {len(df_pandas)}")

        # 3. Spark İşlemleri
        logger.info("Spark oturumu yonetiliyor...")
        spark = SparkSession.builder.appName("Ingestion_Layer").getOrCreate()
        spark_df = spark.createDataFrame(df_pandas)

        # 4. Kaydetme (Bronze/Raw Katmanı)
        # Staging ve Disaster Recovery hazırlığı 
        raw_output_dir = root_dir / "data" / "raw"
        raw_output_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = raw_output_dir / "usd_kur_raw.parquet"
        
        #  Idempotency (Aynı girdiyle her zaman aynı sonuç) 
        logger.info(f"Veri raw katmanina yaziliyor: {output_path}")
        spark_df.write.mode("overwrite").parquet(str(output_path))
        
        logger.info("BAŞARILI: Ingestion sureci tamamlandi ve ham veri muhurlendi.")

    except Exception as e:
        # Hata izole etme ve detaylı raporlama 
        logger.error(f"Ingestion surecinde beklenmedik KRITIK HATA: {str(e)}")
        raise e

if __name__ == "__main__":
    run_ingestion()