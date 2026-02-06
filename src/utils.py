import os
from pyspark.sql import SparkSession
from dotenv import load_dotenv

# Ana dizindeki .env dosyasını bul ve yükle
def load_env_vars():
    # Bu script src içinde olduğu için bir üst dizine bakıyoruz
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dotenv_path = os.path.join(base_dir, '.env')
    load_dotenv(dotenv_path)

def get_spark_session(app_name="FinancialDataPlatform"):
    """
    Spark Session'ı başlatan merkezi fonksiyon.
    master("local") burada tanımlanmazsa, dışarıdan spark-submit ile yönetilebilir.
    """
    return SparkSession.builder \
        .appName(app_name) \
        .config("spark.sql.parquet.compression.codec", "snappy") \
        .getOrCreate()