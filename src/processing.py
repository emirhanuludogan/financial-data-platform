import os
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date
# 1. GÜNCELLEME: Merkezi logger'ı dahil ediyoruz (Sistemin sesi)
from src.utils import get_logger 

# Logger'ı bu katman için isimlendiriyoruz
logger = get_logger("Processing_Silver")

# Windows Spark Ayarı
os.environ['PYSPARK_PYTHON'] = sys.executable
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable

def run_processing():
    # 2. GÜNCELLEME: Başlangıcı mühürlüyoruz (Observability başlangıcı)
    logger.info("ADIM 2: Silver (Processing) sureci baslatildi.")

    try:
        # Spark Session Başlat
        spark = SparkSession.builder.appName("Financial_Processing").getOrCreate()
        
        # Dinamik Yol Belirleme
        current_script_path = os.path.abspath(__file__)
        src_dir = os.path.dirname(current_script_path)
        root_dir = os.path.dirname(src_dir)
        
        raw_path = os.path.join(root_dir, "data", "raw", "usd_kur_raw.parquet")
        
        # 3. GÜNCELLEME: Dosya kontrolünü logger ile yapıyoruz (Error Handling) 
        if not os.path.exists(raw_path):
            logger.error(f"KRITIK HATA: {raw_path} bulunamadi! Ingestion katmani kontrol edilmeli.")
            return

        # Ham Veriyi Oku
        logger.info(f"Raw verisi okunuyor: {raw_path}")
        df = spark.read.parquet(raw_path)
        
        # 4. GÜNCELLEME: Okunan veri hacmini logluyoruz (Volume Metrics) 
        raw_count = df.count()
        logger.info(f"Raw katmanindan {raw_count} satir veri yuklendi.")

        # 5. TEMİZLEME (Cleaning)
        #  Veri kalitesini artırmak için tipleştirme ve temizlik yapıyoruz 
        logger.info("Veri donusturme (Transformation) islemleri uygulaniyor...")
        
        cleaned_df = df.withColumn("Date", to_date(col("Tarih"), "dd-MM-yyyy")) \
                       .filter(col("TP_DK_USD_S_YTL").isNotNull()) \
                       .select(
                           col("Date"), 
                           col("TP_DK_USD_S_YTL").cast("double").alias("USD_Satis")
                       )

        # 6. GÜNCELLEME: Filtreleme sonrası veri kaybını takip ediyoruz (Data Quality check) 
        cleaned_count = cleaned_df.count()
        logger.info(f"Temizlik sonrasi {cleaned_count} gecerli satir kaldi. (Silinen Null: {raw_count - cleaned_count})")

        # Silver Klasörüne Kaydet
        output_path = os.path.join(root_dir, "data", "silver", "usd_kur_cleaned.parquet")
        
        # 7. GÜNCELLEME: Yazma işlemini mühürlüyoruz (Idempotency teyidi)
        logger.info(f"Silver veri Parquet olarak kaydediliyor: {output_path}")
        cleaned_df.write.mode("overwrite").parquet(output_path)
        
        logger.info("Silver katmani islemi basariyla tamamlandi.")

    except Exception as e:
        # 8. GÜNCELLEME: Beklenmedik hataları yakalayıp troubleshoot için logluyoruz 
        logger.error(f"Processing (Silver) asamasinda BEKLENMEDIK HATA: {str(e)}")
        raise e

if __name__ == "__main__":
    run_processing()