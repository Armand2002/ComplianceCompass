#!/bin/sh

# Attendi che il database sia pronto
echo "Attesa per il database..."
while ! curl -s http://db:5432/ >/dev/null; do
  sleep 1
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