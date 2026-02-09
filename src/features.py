import os
import sys
import shutil
from pathlib import Path
from pyspark.sql import SparkSession
from pyspark.sql.window import Window
from pyspark.sql.functions import col, lag, round, isnan
from src.utils import get_logger 

logger = get_logger("Features_Gold")

os.environ['PYSPARK_PYTHON'] = sys.executable
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable

def run_features():
    logger.info("ADIM 3: Gold (Feature Engineering) süreci başlatıldı.")
    
    try:
        spark = SparkSession.builder.appName("Gold_Layer_Features").getOrCreate()
        
        # --- ROOT DİZİN BELİRLEME ---
        current_file = Path(__file__).resolve()
        root_dir = next((p for p in current_file.parents if p.name == "FinancialDataPlatform"), current_file.parents[2])

        input_path = root_dir / "data" / "silver" / "usd_kur_cleaned.parquet"
        output_path = root_dir / "data" / "gold" / "usd_kur_features.parquet"
        
        if not input_path.exists():
            logger.error(f"KRİTİK HATA: Silver verisi bulunamadı: {input_path}")
            return

        # 1. Silver Veriyi Oku
        df = spark.read.parquet(str(input_path))

        # 2. FEATURE ENGINEERING
        logger.info("Analitik hesaplamalar yapılıyor...")
        df_filtered = df.filter(~isnan(col("USD_Satis")))
        windowSpec = Window.orderBy("Date")

        gold_df = df_filtered.withColumn("Prev_USD_Satis", lag("USD_Satis", 1).over(windowSpec)) \
                    .withColumn("Daily_Change_Pct", 
                                round(((col("USD_Satis") - col("Prev_USD_Satis")) / col("Prev_USD_Satis")) * 100, 2)) \
                    .na.fill(0)

        # 3. GÜVENLİ YAZMA (Windows Kilitlerini Baypas Etme)
        if output_path.exists():
            shutil.rmtree(str(output_path), ignore_errors=True)

        logger.info(f"Gold veri mühürleniyor: {output_path}")
        
        # coalesce(1) ile tek dosya çıkartarak Windows'un kilit dosyası yükünü bitiriyoruz
        gold_df.coalesce(1).write.mode("overwrite").parquet(str(output_path))
        
        logger.info("BAŞARILI: Gold katmanı ve tüm pipeline tamamlandı!")

    except Exception as e:
        logger.error(f"Gold aşamasında KRİTİK HATA: {str(e)}")
        raise e

if __name__ == "__main__":
    run_features()