import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from evds import evdsAPI
from pyspark.sql import SparkSession

# 1. Ortam ve Yol Yapılandırması (Pathlib ile kesin çözüm)
# Path(__file__) -> src/ingestion/ingestion.py
# .parents[2]    -> FinancialDataPlatform (Root)
root_dir = Path(__file__).resolve().parents[2]
dotenv_path = root_dir / ".env"

# .env dosyasını yükle
load_dotenv(dotenv_path=dotenv_path)

# Windows Spark Ayarları
os.environ['PYSPARK_PYTHON'] = sys.executable
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable

def run_ingestion():
    api_key = os.getenv("EVDS_API_KEY")
    
    # Debug çıktıları
    print(f"--- Sistem Kontrolü ---")
    print(f"Root Dizini: {root_dir}")
    print(f"API Anahtarı: {api_key[:4]}***" if api_key else "API ANAHTARI BULUNAMADI!")
    
    if not api_key:
        return

    # 2. Veri Çekme
    evds = evdsAPI(api_key)
    print("EVDS'den veri çekiliyor...")
    df_pandas = evds.get_data(["TP.DK.USD.S.YTL"], startdate="01-01-2024", enddate="01-01-2026")
    
    # 3. Spark İşlemleri
    spark = SparkSession.builder.appName("Ingestion_Layer").getOrCreate()
    spark_df = spark.createDataFrame(df_pandas)
    
    # 4. Kaydet (Data/Raw)
    # Klasör yoksa oluşturur
    raw_output_dir = root_dir / "data" / "raw"
    raw_output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = raw_output_dir / "usd_kur_raw.parquet"
    spark_df.write.mode("overwrite").parquet(str(output_path))
    
    print(f"BAŞARILI: Ham veri kaydedildi -> {output_path}")

if __name__ == "__main__":
    run_ingestion()