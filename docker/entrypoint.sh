#!/bin/bash
# docker/entrypoint.sh - Rimozione controllo Elasticsearch
set -e

# Funzione per verificare servizi
check_service() {
    local service=$1
    local host=$2
    local port=$3
    local max_retries=$4
    local retry_count=0
    
    echo "Verifica disponibilità di $service su $host:$port..."
    while ! nc -z $host $port && [ $retry_count -lt $max_retries ]; do
        retry_count=$((retry_count+1))
        echo "$service non disponibile, attendo... ($retry_count/$max_retries)"
        sleep 3
    done
    
    if [ $retry_count -eq $max_retries ]; then
        echo "ERRORE: $service non disponibile dopo $max_retries tentativi!"
        return 1
    else
        echo "$service disponibile!"
        return 0
    fi
}

# Estrai parametri dal DATABASE_URL o usa valori predefiniti
if [ -n "$DATABASE_URL" ]; then
    # Estrai host e porta dal DATABASE_URL 
    DB_HOST=$(echo $DATABASE_URL | sed -e 's/^.*@\(.*\):.*/\1/')
    DB_PORT=$(echo $DATABASE_URL | sed -e 's/^.*:\([0-9]*\)\/.*/\1/')
else
    # Valori predefiniti
    DB_HOST="db"
    DB_PORT="5432"
fi

# Attendi disponibilità database
check_service "PostgreSQL" "$DB_HOST" "$DB_PORT" "30" || exit 1

# Esegui migrazioni
echo "Esecuzione migrazioni database..."
alembic upgrade head

# Avvia l'applicazione
echo "Avvio applicazione..."
exec "$@"