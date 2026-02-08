import os
import sys
import logging
from pyspark.sql import SparkSession
from dotenv import load_dotenv

# 1. LOGGING KURULUMU (Kitap Prensibi: Centralized Logging)
def get_logger(name):
    """
    Sistemin her adımı için tarih mühürlü günlük tutar. [cite: 1335]
    Bu fonksiyon olmazsa main.py hata verir.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        # Zaman - Kaynak - Seviye - Mesaj formatı
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        
        # Konsol çıktısı
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Dosya çıktısı (logs/pipeline.log)
        if not os.path.exists('logs'):
            os.makedirs('logs')
        file_handler = logging.FileHandler('logs/pipeline.log', encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    return logger

# 2. ORTAM DEĞİŞKENLERİ (Environment Configuration)
def load_env_vars():
    """
    Ana dizindeki .env dosyasını bulur ve yükler.
    """
    # src içinden bir üst dizine (root) çıkış
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dotenv_path = os.path.join(base_dir, '.env')
    load_dotenv(dotenv_path)

# 3. SPARK YAPILANDIRMASI (Efficiency Prensibi)
def get_spark_session(app_name="FinancialDataPlatform"):
    """
    Merkezi Spark Session başlatıcı. 
    Snappy sıkıştırma kullanarak verimliliği (Efficiency) artırır. [cite: 1463]
    """
    # Windows üzerinde Spark çalışması için gerekli Python yolları
    os.environ['PYSPARK_PYTHON'] = sys.executable
    os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable
    
    return SparkSession.builder \
        .appName(app_name) \
        .config("spark.sql.parquet.compression.codec", "snappy") \
        .getOrCreate()