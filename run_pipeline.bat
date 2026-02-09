@echo off
:: 1. Adim: Dosyanin bulundugu klasore otomatik odaklan
cd /d "%~dp0"

:: 2. Adim: Klasore girdigimizi teyit edelim
echo Mevcut Konum: %cd%

:: 3. Adim: Log klasoru yoksa olustur
if not exist logs mkdir logs

:: 4. Adim: Python scriptini calistir
python main.py >> logs\automation.log 2>&1

:: 5. Adim: Bitisi logla
echo [%date% %time%] Otomatik calistirma basarili. >> logs\automation.log