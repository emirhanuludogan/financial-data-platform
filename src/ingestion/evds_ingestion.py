from evds import evdsAPI
from pyspark.sql import SparkSession

# EVDS API Key
API_KEY = "xZJ30MxLIp"

# EVDS bağlantısı
evds = evdsAPI(API_KEY)

# EVDS'den veri çekme
df = evds.get_data(
    series=["TP.DK.USD.S.YTL"],
    startdate="01-01-2024",
    enddate="31-01-2024",
    frequency=1,
    aggregation_types="avg"
)

# Spark session oluşturma
spark = SparkSession.builder \
    .appName("EVDS_Data_Engineering") \
    .getOrCreate()

# Pandas DataFrame -> PySpark DataFrame
spark_df = spark.createDataFrame(df)

# Kontrol amaçlı gösterim
spark_df.show()
from pyspark.sql import SparkSession
print("PYSPARK OK")
  