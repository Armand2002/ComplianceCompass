#!/bin/sh

set -e

# Definisci un limite ai tentativi di connessione
MAX_RETRIES=30
RETRY_COUNT=0
CONNECTION_TIMEOUT=5

# Configurazione logging
log_info() {
    echo "[INFO] $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warning() {
    echo "[WARNING] $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo "[ERROR] $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Verifica ambiente
if [ -z "$DATABASE_URL" ]; then
    log_error "DATABASE_URL non configurato nell'ambiente"
    exit 1
fi

# Funzione di verifica del database
wait_for_database() {
    log_info "Attesa per il database PostgreSQL..."
    
    until pg_isready -h db -U postgres -t $CONNECTION_TIMEOUT || [ $RETRY_COUNT -eq $MAX_RETRIES ]; do
        log_info "Il database non è ancora pronto - attendo... ($RETRY_COUNT/$MAX_RETRIES)"
        RETRY_COUNT=$((RETRY_COUNT+1))
        sleep 2
    done

    if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
        log_error "Impossibile connettersi al database dopo $MAX_RETRIES tentativi."
        return 1
    fi

    log_info "Database PostgreSQL disponibile!"
    return 0
}

# Funzione di verifica di Elasticsearch
wait_for_elasticsearch() {
    if [ -z "$ELASTICSEARCH_URL" ]; then
        log_warning "ELASTICSEARCH_URL non configurato, saltando verifica Elasticsearch"
        return 0
    fi
    
    log_info "Verifica della disponibilità di Elasticsearch..."
    RETRY_COUNT=0
    
    until curl --silent --fail "$ELASTICSEARCH_URL/_cluster/health" > /dev/null || [ $RETRY_COUNT -eq $MAX_RETRIES ]; do
        log_info "Elasticsearch non è ancora pronto - attendo... ($RETRY_COUNT/$MAX_RETRIES)"
        RETRY_COUNT=$((RETRY_COUNT+1))
        sleep 3
    done

    if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
        log_warning "Elasticsearch non disponibile dopo $MAX_RETRIES tentativi. L'applicazione continuerà con funzionalità ridotte."
        return 0
    fi

    log_info "Elasticsearch disponibile!"
    return 0
}

# Verificare disponibilità del database e proseguire solo se disponibile
wait_for_database || exit 1

# Verifica Elasticsearch in modalità non bloccante
wait_for_elasticsearch

# Esegui migrazioni del database
log_info "Esecuzione migrazioni del database..."
if alembic upgrade head; then
    log_info "Migrazioni completate con successo"
else
    log_error "Si sono verificati problemi durante le migrazioni"
    log_warning "L'applicazione potrebbe non funzionare correttamente"
fi

# Inizializza dati di base se necessario
log_info "Inizializzazione dati di base..."
if python -m scripts.seed_db; then
    log_info "Inizializzazione dati completata con successo"
else
    log_warning "Si sono verificati problemi durante l'inizializzazione dei dati"
    log_warning "Alcune funzionalità potrebbero non essere disponibili"
fi

# Avvia l'applicazione
log_info "Avvio dell'applicazione..."
exec "$@"