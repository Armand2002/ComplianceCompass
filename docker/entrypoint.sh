#!/bin/sh

# Attendi che il database sia pronto
echo "Attesa per il database..."
export PGPASSWORD=$POSTGRES_PASSWORD
until pg_isready -h db -U postgres; do
  echo "Il database non è ancora pronto - attendo..."
  sleep 2
done
echo "Database disponibile!"

# Esegui migrazioni
echo "Esecuzione migrazioni del database..."
alembic upgrade head

# Inizializza dati di base se necessario
echo "Inizializzazione dati di base..."
python -m scripts.seed_db

# Avvia l'applicazione
echo "Avvio dell'applicazione..."
exec "$@"