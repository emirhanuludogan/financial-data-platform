import os
import sys
from pathlib import Path
from pyspark.sql import SparkSession
from pyspark.sql.window import Window
from pyspark.sql.functions import col, lag, round, when, isnan
# 1. GÜNCELLEME: Merkezi logger'ı sisteme dahil ediyoruz
from src.utils import get_logger 

# Logger'ı bu katman (Gold) özelinde isimlendiriyoruz
logger = get_logger("Features_Gold")

# Windows Spark Ayarı
os.environ['PYSPARK_PYTHON'] = sys.executable
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable

def run_features():
    # 2. GÜNCELLEME: Analitik sürecin başladığını mühürlüyoruz (Observability)
    logger.info("ADIM 3: Gold (Feature Engineering) süreci başlatıldı.")
    
    try:
        spark = SparkSession.builder.appName("Gold_Layer_Features").getOrCreate()
        
      # 1. Yolları Belirle
        # parents[1] sizi src'den ana dizine (FinancialDataPlatform) çıkarır.
        root_dir = Path(__file__).resolve().parents[1] 
        
        input_path = root_dir / "data" / "silver" / "usd_kur_cleaned.parquet"
        # 2. Silver Veriyi Oku
        #  Veri kaynağının (Silver) varlığını teyit et
        if not input_path.exists():
            logger.error(f"KRİTİK HATA: Silver verisi bulunamadı: {input_path}")
            return

        logger.info(f"Silver katmanı okunuyor: {input_path}")
        df = spark.read.parquet(str(input_path))

        # 3. FEATURE ENGINEERING
        #  Dönüşüm (Transformation) adımlarını detaylıca logla
        logger.info("Feature Engineering işlemleri başlıyor (Daily Change Pct)...")
        
        # Hafta sonu boşluklarını temizle
        df_filtered = df.filter(~isnan(col("USD_Satis")))
        
        # Pencere oluştur
        windowSpec = Window.orderBy("Date")

        # Değişim yüzdesini hesapla
        # Kitap Prensibi: Complex mutation (lag) takibi
        gold_df = df_filtered.withColumn("Prev_USD_Satis", lag("USD_Satis", 1).over(windowSpec)) \
                    .withColumn("Daily_Change_Pct", 
                                round(((col("USD_Satis") - col("Prev_USD_Satis")) / col("Prev_USD_Satis")) * 100, 2)) \
                    .na.fill(0) # İlk satır kontrolü

        # 4. GÜNCELLEME: Veri kalitesi doğrulaması (Data Quality Check)
        final_count = gold_df.count()
        logger.info(f"Gold katmanı hesaplamaları tamamlandı. Toplam kayıt: {final_count}")

        # 5. KAYDET (Gold Layer)
        # Kitap Prensibi: Son ürünün (Gold) analiz hazır olduğunu mühürle
        output_path = root_dir / "data" / "gold" / "usd_kur_features.parquet"
        
        logger.info(f"Gold veri Parquet olarak kaydediliyor: {output_path}")
        gold_df.write.mode("overwrite").parquet(str(output_path))
        
        logger.info("BAŞARILI: Gold katmanı hazır ve analiz edilebilir durumda.")

    except Exception as e:
        # 6. GÜNCELLEME: İş mantığı hatalarını troubleshooting için logla
        logger.error(f"Features (Gold) aşamasında beklenmedik HATA: {str(e)}")
        raise e

if __name__ == "__main__":
    run_features()

