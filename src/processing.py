import os
import sys
import shutil
from pathlib import Path
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date
from src.utils import get_logger 

logger = get_logger("Processing_Silver")

os.environ['PYSPARK_PYTHON'] = sys.executable
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable

def run_processing():
    logger.info("ADIM 2: Silver (Processing) sureci baslatildi.")

    try:
        spark = SparkSession.builder.appName("Financial_Processing").getOrCreate()
        
        # --- ROOT DİZİN BELİRLEME ---
        current_file = Path(__file__).resolve()
        root_dir = next((p for p in current_file.parents if p.name == "FinancialDataPlatform"), current_file.parents[2])

        raw_path = root_dir / "data" / "raw" / "usd_kur_raw.parquet"
        silver_path = root_dir / "data" / "silver" / "usd_kur_cleaned.parquet"
        
        if not raw_path.exists():
            logger.error(f"KRITIK HATA: {raw_path} bulunamadi!")
            return

        # 1. Veri Okuma
        df = spark.read.parquet(str(raw_path))
        
        # 2. Temizleme ve Dönüştürme
        cleaned_df = df.withColumn("Date", to_date(col("Tarih"), "dd-MM-yyyy")) \
                       .filter(col("TP_DK_USD_S_YTL").isNotNull()) \
                       .select(
                           col("Date"), 
                           col("TP_DK_USD_S_YTL").cast("double").alias("USD_Satis")
                       )

        # 3. GÜVENLİ YAZMA (Windows Kilitlerini Baypas Etme)
        # Klasör varsa Spark hata vermesin diye sessizce temizliyoruz
        if silver_path.exists():    
            shutil.rmtree(str(silver_path), ignore_errors=True) 

        logger.info(f"Silver veri mühürleniyor: {silver_path}")
        
        # coalesce(1) + overwrite: Windows'ta hata payını sıfıra indirir
        cleaned_df.coalesce(1).write.mode("overwrite").parquet(str(silver_path))
        
        logger.info("BAŞARILI: Silver katmanı tamamlandı.")

    except Exception as e:
        logger.error(f"Silver aşamasında KRİTİK HATA: {str(e)}")
        raise e

if __name__ == "__main__":
    run_processing()