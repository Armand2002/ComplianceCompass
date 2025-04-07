REM filepath: c:\Users\arman\Desktop\ComplianceCompass\ComplianceCompass\run.bat
@echo off
REM Script di avvio completo con Elasticsearch migliorato

echo ==================================
echo ComplianceCompass - Avvio ambiente
echo ==================================

REM Verifica prerequisiti
echo Verifico i prerequisiti...

REM Verifica Docker
echo Verifico che Docker sia in esecuzione...
docker info >nul 2>&1
if %errorlevel% neq 0 (
  echo [ERRORE] Docker non è in esecuzione.
  echo Per favore, avvia Docker Desktop e riprova.
  goto :error
)

REM Verifica file di configurazione
echo Verifico presenza file di configurazione...
IF NOT EXIST .env (
  copy .env.example .env
  echo [INFO] File .env creato da template
)

REM Verifica presence di alembic.ini
echo Verifica presenza di alembic.ini...
IF NOT EXIST alembic.ini (
  echo [ATTENZIONE] File alembic.ini mancante
  echo Creazione file alembic.ini base...
  copy alembic.ini.example alembic.ini
  if %errorlevel% neq 0 (
    echo [ERRORE] Impossibile creare alembic.ini
    goto :error
  ) else (
    echo [INFO] File alembic.ini creato
  )
)

REM Arresta container esistenti
echo Arresto container esistenti...
docker-compose down

REM Chiedi se ricostruire i container
SET REBUILD=N
SET /P REBUILD="Ricostruire i container? (s/N): "
if /I "%REBUILD%"=="s" (
  echo Avvio costruzione container...
  docker-compose build
  if %errorlevel% neq 0 (
    echo [ERRORE] Costruzione container fallita
    goto :error
  )
) else (
  echo Uso immagini esistenti...
)

REM Avvio container
echo Avvio ambiente di sviluppo completo...
docker-compose up
if %errorlevel% neq 0 (
  echo [ERRORE] Impossibile avviare i container
  goto :error
)

goto :end

:error
echo ==================================
echo [ERRORE] Avvio fallito
echo ==================================
exit /b 1

:end
echo ==================================
echo Ambiente terminato
echo ==================================
exit /b 0