import sys
import os
import time
# 1. GÜNCELLEME: Merkezi logger ve alt scriptlerin içeri aktarılması
from src.utils import get_logger
from src.ingestion.ingestion import run_ingestion
from src.processing import run_processing
from src.features import run_features

# Şef logger'ı başlatıyoruz (Sistemin ana orkestratörü)
logger = get_logger("Orchestrator_Main")

def main():
    # 2. GÜNCELLEME: Toplam çalışma süresini ölçmek için başlangıç zamanı (Efficiency metriği)
    start_time = time.time()
    
    # Pipeline başlangıcının açıkça mühürlenmesi (Observability)
    logger.info("=== ETL PIPELINE BASLATILDI ===")

    try:
        # 3. GÜNCELLEME: Adımlar arası geçişlerin ve bağımlılıkların yönetimi (Dependency Management)
        # 1. Adım: Veri Çekme (Bronze/Raw)
        logger.info(">>> ADIM 1: Ingestion (Raw) süreci tetikleniyor...")
        run_ingestion()
        logger.info(">>> ADIM 1: Ingestion başarıyla tamamlandı.")
        
        # 2. Adım: Temizleme ve Tipleştirme (Silver/Processed)
        # Sequential steps (Sıralı adımların korunması)
        logger.info(">>> ADIM 2: Processing (Silver) süreci tetikleniyor...")
        run_processing()
        logger.info(">>> ADIM 2: Processing başarıyla tamamlandı.")
        
        # 3. Adım: Özellik Mühendisliği ve Analiz (Gold/Analytics)
        #  Business value creation (Değer üretme aşaması)
        logger.info(">>> ADIM 3: Features (Gold) süreci tetikleniyor...")
        run_features()
        logger.info(">>> ADIM 3: Features başarıyla tamamlandı.")
        
        # 4. GÜNCELLEME: Toplam süreyi hesapla ve bitişi mühürle
        end_time = time.time()
        total_duration = round(end_time - start_time, 2)
        
        logger.info(f"=== ETL SURECI BASARIYLA TAMAMLANDI (Sure: {total_duration} saniye) ===")

    except Exception as e:
        # 5. GÜNCELLEME: Merkezi hata yakalama (Centralized Error Handling)
        #  Hataları sessizce geçiştirme, mühürle ve sistemi güvenli durdur.
        logger.critical(f"!!! PIPELINE KRITIK HATA ILE DURDURULDU: {str(e)}")
        # Troubleshooting için hatayı fırlatıyoruz
        sys.exit(1)

if __name__ == "__main__":
    main()