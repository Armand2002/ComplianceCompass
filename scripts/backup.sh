#!/bin/bash
# scripts/backup.sh - Backup del codice e del database prima delle modifiche

set -e

# Configurazione
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="./backups/${TIMESTAMP}"
DB_CONTAINER="db"  # Nome del container del database
DB_NAME="compliance_compass"
DB_USER="postgres"

# Creazione directory di backup
mkdir -p "${BACKUP_DIR}/code"
mkdir -p "${BACKUP_DIR}/database"

echo "=== Compliance Compass Backup ==="
echo "Timestamp: ${TIMESTAMP}"
echo "Directory: ${BACKUP_DIR}"

# 1. Backup del codice
echo "Esecuzione backup del codice..."
git archive --format=tar HEAD | tar -x -C "${BACKUP_DIR}/code"

# 2. Backup del database
echo "Esecuzione backup del database..."
docker-compose exec ${DB_CONTAINER} pg_dump -U ${DB_USER} ${DB_NAME} > "${BACKUP_DIR}/database/db_dump.sql"

# 3. Salvataggio versioni e dipendenze
pip freeze > "${BACKUP_DIR}/requirements_snapshot.txt"
docker-compose config > "${BACKUP_DIR}/docker_compose_snapshot.yml"

echo "Backup completato con successo!"
echo "Database: ${BACKUP_DIR}/database/db_dump.sql"
echo "Codice: ${BACKUP_DIR}/code/"