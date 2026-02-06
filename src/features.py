import os
import sys
from pathlib import Path
from pyspark.sql import SparkSession
from pyspark.sql.window import Window
from pyspark.sql.functions import col, lag, round, when, isnan

# Windows Spark Ayarı
os.environ['PYSPARK_PYTHON'] = sys.executable
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable

def run_features():
    spark = SparkSession.builder.appName("Gold_Layer_Features").getOrCreate()
    
    # 1. Yolları Belirle
    root_dir = Path(__file__).resolve().parents[1]
    input_path = root_dir / "data" / "silver" / "usd_kur_cleaned.parquet"
    
    # 2. Silver Veriyi Oku
    print(f"Gold katmanı için veri okunuyor: {input_path}")
    df = spark.read.parquet(str(input_path))

    # 3. FEATURE ENGINEERING
    # Hafta sonu boşluklarını (NaN) temizle
    df_filtered = df.filter(~isnan(col("USD_Satis")))

    # Tarihe göre sıralı pencere oluştur
    windowSpec = Window.orderBy("Date")

    # Değişim yüzdesini hesapla
    gold_df = df_filtered.withColumn("Prev_USD_Satis", lag("USD_Satis", 1).over(windowSpec)) \
                .withColumn("Daily_Change_Pct", 
                            round(((col("USD_Satis") - col("Prev_USD_Satis")) / col("Prev_USD_Satis")) * 100, 2)) \
                .na.fill(0) # İlk satırdaki null değerini 0 yap

    # 4. KAYDET (Gold Layer)
    output_path = root_dir / "data" / "gold" / "usd_kur_features.parquet"
    gold_df.write.mode("overwrite").parquet(str(output_path))
    
    print(f"--- GOLD LAYER HAZIR ---")
    gold_df.orderBy(col("Date").desc()).show(10)

if __name__ == "__main__":
    run_features()