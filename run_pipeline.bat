@echo off
:: 1. Adim: Dosyanin bulundugu klasore otomatik odaklan
cd /d "%~dp0"

:: 2. Adim: Klasore girdigimizi teyit edelim
echo Mevcut Konum: %cd%

:: 3. Adim: Log klasoru yoksa olustur
if not exist logs mkdir logs

:: 4. Adim: Varsa proje ortamini kullan, modulu calistir
set "PIPELINE_PYTHON=python"
if exist ".venv\Scripts\python.exe" set "PIPELINE_PYTHON=.venv\Scripts\python.exe"
"%PIPELINE_PYTHON%" -m src.pipelines.main >> logs\automation.log 2>&1
set "PIPELINE_EXIT_CODE=%ERRORLEVEL%"

:: 5. Adim: Gercek sonuc kodunu logla ve cagirani bilgilendir
if "%PIPELINE_EXIT_CODE%"=="0" (
    echo [%date% %time%] Otomatik calistirma basarili. >> logs\automation.log
) else (
    echo [%date% %time%] Otomatik calistirma basarisiz. Cikis kodu: %PIPELINE_EXIT_CODE% >> logs\automation.log
)
exit /b %PIPELINE_EXIT_CODE%
