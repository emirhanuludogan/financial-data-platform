import logging
import sys
import os

def get_logger(name):
    """
     'verbose logging' sayesinde akış - zaman - katman takibi yaptım. 
    hem konsola hem de dosyaya yazan merkezi logger. 
    """
    logger = logging.getLogger(name)
    
    # Eğer logger zaten konfigüre edildiyse tekrar etme
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Format: Zaman - Kaynak Script - Mesaj Seviyesi - Mesaj
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # 1. Konsol Handler (PowerShell'de anlık görmek için)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # 2. Dosya Handler (Geriye dönük hata ayıklama/audit için) 
        # Proje ana dizininde 'logs' klasörü oluşturur
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        file_handler = logging.FileHandler('logs/pipeline.log', encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger