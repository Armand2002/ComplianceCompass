#!/bin/sh

set -e

# Definisci un limite ai tentativi di connessione
MAX_RETRIES=30
RETRY_COUNT=0

echo "Attesa per il database..."
until pg_isready -h db -U postgres || [ $RETRY_COUNT -eq $MAX_RETRIES ]; do
  echo "Il database non è ancora pronto - attendo... ($RETRY_COUNT/$MAX_RETRIES)"
  RETRY_COUNT=$((RETRY_COUNT+1))
  sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
  echo "Impossibile connettersi al database dopo $MAX_RETRIES tentativi. Uscita."
  exit 1
fi

echo "Database disponibile!"

# Esegui migrazioni
echo "Esecuzione migrazioni del database..."
alembic upgrade head || echo "Attenzione: Errore con le migrazioni, ma continuiamo comunque"

# Inizializza dati di base se necessario
echo "Inizializzazione dati di base..."
python -m scripts.seed_db || echo "Avviso: Si sono verificati errori durante il seeding del database, ma l'applicazione verrà comunque avviata"

# Avvia l'applicazione
echo "Avvio dell'applicazione..."
exec "$@"