#!/bin/bash
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

# Attendi disponibilità database
check_service "PostgreSQL" "db" "5432" "30" || exit 1

# Attendi disponibilità elasticsearch (con gestione errori)
if ! check_service "Elasticsearch" "elasticsearch" "9200" "30"; then
    echo "AVVISO: Elasticsearch non disponibile, proseguo con funzionalità limitate."
fi

# Esegui migrazioni
echo "Esecuzione migrazioni database..."
alembic upgrade head

# Avvia l'applicazione
echo "Avvio applicazione..."
exec "$@"