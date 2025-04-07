#!/bin/bash
# Entrypoint script for Compliance Compass API

# Exit on any error
set -e

# Print commands for debugging
# set -x

# Logging function
log() {
    echo "[ENTRYPOINT] $1"
}

# Wait for database to be ready
wait_for_database() {
    local host="${DB_HOST:-db}"
    local port="${DB_PORT:-5432}"
    local max_attempts=30
    local attempt=1

    log "Waiting for database on $host:$port..."

    while [ $attempt -le $max_attempts ]; do
        if nc -z "$host" "$port"; then
            log "Database is ready!"
            return 0
        fi

        log "Waiting for database... (Attempt $attempt/$max_attempts)"
        sleep 2
        attempt=$((attempt + 1))
    done

    log "Database connection failed after $max_attempts attempts"
    return 1
}

# Run database migrations
run_migrations() {
    log "Running database migrations..."
    alembic upgrade head
}

# Seed database
seed_database() {
    log "Seeding database..."
    
    # Determine seeding strategy based on environment
    local seed_args=""
    if [ "$ENVIRONMENT" = "production" ]; then
        seed_args="--admin-only"
    fi
    
    python -m scripts.seed_db $seed_args
}

# Main startup sequence
main() {
    # Set default environment if not set
    export ENVIRONMENT="${ENVIRONMENT:-development}"
    export DEBUG="${DEBUG:-true}"

    # Wait for database
    if ! wait_for_database; then
        log "Could not connect to database. Exiting."
        exit 1
    fi

    # Run migrations
    run_migrations

    # Seed database
    seed_database

    # Start the application
    log "Starting Compliance Compass API..."
    
    # Use exec to replace the current process
    exec uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
}

# Call main with all script arguments
main "$@"