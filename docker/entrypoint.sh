#!/bin/sh

# Attendi che il database sia pronto, con timeout
echo "Attesa per il database..."
export PGPASSWORD=$POSTGRES_PASSWORD

# Definisci un limite ai tentativi di connessione
MAX_RETRIES=30
RETRY_COUNT=0

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
if ! alembic upgrade head; then
  echo "Errore durante l'esecuzione delle migrazioni!"
  exit 1
fi

# Inizializza dati di base se necessario
echo "Inizializzazione dati di base..."
if ! python -m scripts.seed_db; then
  echo "Avviso: Si sono verificati errori durante il seeding del database, ma l'applicazione verrà comunque avviata"
  # Non usciamo con errore per permettere comunque l'avvio dell'app
fi

# Avvia l'applicazione
echo "Avvio dell'applicazione..."
exec "$@"