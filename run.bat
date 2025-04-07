@echo off
REM Script di avvio completo con Elasticsearch

echo Verifico presenza file di configurazione...
IF NOT EXIST .env (
  copy .env.example .env
  echo File .env creato
)

echo Verifico che Docker sia in esecuzione...
docker info >nul 2>&1
if %errorlevel% neq 0 (
  echo ERRORE: Docker non è in esecuzione.
  echo Per favore, avvia Docker Desktop e riprova.
  exit /b 1
)

echo Verifica presenza di alembic.ini...
IF NOT EXIST alembic.ini (
  echo Creazione file alembic.ini
  copy NUL alembic.ini
)

echo Arresto container esistenti...
docker-compose down

SET /P REBUILD="Ricostruire i container? (s/N): "
if /I "%REBUILD%"=="s" (
  echo Avvio costruzione container...
  docker-compose build
) else (
  echo Uso immagini esistenti...
)

echo Avvio ambiente di sviluppo completo...
docker-compose up