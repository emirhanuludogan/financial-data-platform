import os
import sys
from dotenv import load_dotenv
from evds import evdsAPI
from pyspark.sql import SparkSession

# ----------------------------
# Spark Ortam Yapılandırması
# ----------------------------
# Windows üzerinde Spark'ın Python'u bulabilmesi için gerekli
os.environ['PYSPARK_PYTHON'] = sys.executable
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable

# ----------------------------
# Yapılandırma Yükleme (.env)
# ----------------------------
current_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(current_dir, ".env")
load_dotenv(dotenv_path)

API_KEY = os.getenv("EVDS_API_KEY")  
if not API_KEY:
    raise Exception("Hata: EVDS_API_KEY .env dosyasında bulunamadı!")  

# ----------------------------
# Veri Çekme (EVDS)
# ----------------------------
evds = evdsAPI(API_KEY)
df = evds.get_data(
    series=["TP.DK.USD.S.YTL"],
    startdate="01-01-2024",
    enddate="31-01-2024",
    frequency=1,
    aggregation_types="avg"
)

# ----------------------------
# Spark İşlemleri
# ----------------------------
spark = SparkSession.builder \
    .appName("EVDS_Data_Engineering") \
    .getOrCreate()

# Pandas DataFrame -> PySpark DataFrame  
spark_df = spark.createDataFrame(df)

# Sonuçları Göster    
spark_df.show()

print("Islem Basariyla Tamamlandi.")


