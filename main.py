import sys
import os
from src.ingestion.ingestion import run_ingestion
from src.processing import run_processing
from src.features import run_features

def main():
    # Emojiler kaldırıldı, sadece düz metin bırakıldı
    print("--- ETL Pipeline Baslatiliyor ---\n")

    try:
        # 1. Adım: Veri Çekme (Bronze)
        print("--- 1. ADIM: INGESTION (BRONZE) ---")
        run_ingestion()
        
        # 2. Adım: Temizleme (Silver)
        print("\n--- 2. ADIM: PROCESSING (SILVER) ---")
        run_processing()
        
        # 3. Adım: Özellik Mühendisliği (Gold)
        print("\n--- 3. ADIM: FEATURES (GOLD) ---")
        run_features()
        
        print("\n--- ETL SURECI BASARIYLA TAMAMLANDI ---")

    except Exception as e:
        print(f"\n--- Pipeline Hata Verdi: {str(e)} ---")
        sys.exit(1)

if __name__ == "__main__":
    main()