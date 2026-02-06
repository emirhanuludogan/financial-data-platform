import os
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date

# Windows Spark Ayarı
os.environ['PYSPARK_PYTHON'] = sys.executable
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable

def run_processing():
    # 1. Spark Session Başlat
    spark = SparkSession.builder.appName("Financial_Processing").getOrCreate()
    
    # 2. Dinamik Yol Belirleme (Root Dizinini Bulma)
    current_script_path = os.path.abspath(__file__) # src/processing.py
    src_dir = os.path.dirname(current_script_path)
    root_dir = os.path.dirname(src_dir)
    
    raw_path = os.path.join(root_dir, "data", "raw", "usd_kur_raw.parquet")
    
    if not os.path.exists(raw_path):
        print(f"Hata: {raw_path} bulunamadı! Önce ingestion.py çalışmalı.")
        return

    # 3. Ham Veriyi Oku
    print(f"Silver katmanı için veri okunuyor: {raw_path}")
    df = spark.read.parquet(raw_path)

    # 4. TEMİZLEME (Cleaning)
    # - Tarih sütununu gerçek Date tipine çevir
    # - Döviz sütununu sayısal (double) yap
    # - Boş (null) satırları temizle
    cleaned_df = df.withColumn("Date", to_date(col("Tarih"), "dd-MM-yyyy")) \
                   .filter(col("TP_DK_USD_S_YTL").isNotNull()) \
                   .select(
                       col("Date"), 
                       col("TP_DK_USD_S_YTL").cast("double").alias("USD_Satis")
                   )

    # 5. Silver Klasörüne Kaydet
    output_path = os.path.join(root_dir, "data", "silver", "usd_kur_cleaned.parquet")
    cleaned_df.write.mode("overwrite").parquet(output_path)
    
    print(f"Silver veri hazır! Kayıt yeri: {output_path}")
    cleaned_df.show(5)

if __name__ == "__main__":
    run_processing()