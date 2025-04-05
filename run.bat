@echo off
REM Script per avviare l'ambiente ComplianceCompass

echo Verifico e creo il file .env...
IF NOT EXIST .env (
  copy .env.example .env
  echo File .env creato
) ELSE (
  echo File .env già esistente
)

echo Pulizia ambiente Docker...
docker-compose down
docker system prune -af --volumes

echo Verifico la presenza del file alembic.ini...
IF NOT EXIST alembic.ini (
  echo "Creazione file alembic.ini"
  copy NUL alembic.ini
)

echo Avvio costruzione container...
docker-compose build --no-cache

echo Avvio ambiente di sviluppo...
docker-compose up