import sys
import os
import time

# --- YOL DÜZELTME (PATH FIX) ---
# main.py src/pipelines içinde olduğu için, root dizini (FinancialDataPlatform) ekliyoruz
current_dir = os.path.dirname(os.path.abspath(__file__)) # src/pipelines
project_root = os.path.abspath(os.path.join(current_dir, "../../")) # FinancialDataPlatform

if project_root not in sys.path:
    sys.path.insert(0, project_root)
# ------------------------------

# Artık importlar sorunsuz çalışacaktır
try:
    from src.utils import get_logger
    from src.ingestion.ingestion import run_ingestion
    from src.processing import run_processing
    from src.features import run_features
except ImportError as e:
    print(f"Import Hatası: {e}. Lütfen çalışma dizinini kontrol edin.")
    sys.exit(1)

logger = get_logger("Orchestrator_Main")

def main():
    start_time = time.time()
    logger.info("=== ETL PIPELINE BASLATILDI ===")
    logger.info(f"Root Dizini: {project_root}") # Takip için rootu basalım

    try:
        # 1. Adım: Ingestion
        logger.info(">>> ADIM 1: Ingestion (Raw) süreci tetikleniyor...")
        run_ingestion()
        logger.info(">>> ADIM 1: Ingestion başarıyla tamamlandı.")
        
        # 2. Adım: Processing
        logger.info(">>> ADIM 2: Processing (Silver) süreci tetikleniyor...")
        run_processing()
        logger.info(">>> ADIM 2: Processing başarıyla tamamlandı.")
        
        # 3. Adım: Features
        logger.info(">>> ADIM 3: Features (Gold) süreci tetikleniyor...")
        run_features()
        logger.info(">>> ADIM 3: Features başarıyla tamamlandı.")
        
        end_time = time.time()
        total_duration = round(end_time - start_time, 2)
        logger.info(f"=== ETL SURECI BASARIYLA TAMAMLANDI (Sure: {total_duration} saniye) ===")

    except Exception as e:
        logger.critical(f"!!! PIPELINE KRITIK HATA ILE DURDURULDU: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()