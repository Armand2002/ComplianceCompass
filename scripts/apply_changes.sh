#!/bin/bash
# scripts/apply_changes.sh
# Script per applicare le modifiche di rimozione Elasticsearch e Chatbot

set -e

echo "=== Compliance Compass - Applicazione Modifiche ==="
echo "Rimozione Elasticsearch e Chatbot"
echo

# 1. Controllo setup
if [ ! -f ".env" ]; then
    echo "File .env non trovato. Creazione da template..."
    cp .env.example .env
    echo "File .env creato. Verifica le impostazioni."
fi

# 2. Backup (esecuzione script backup)
echo "Esecuzione backup..."
bash scripts/backup.sh
echo "Backup completato."

# 3. Aggiornamento Docker Compose
echo "Aggiornamento configurazione Docker..."
# Rimozione Elasticsearch da docker-compose.yml
sed -i '/elasticsearch:/,+10d' docker-compose.yml
# Aggiornamento dipendenze api
sed -i 's/- elasticsearch//g' docker-compose.yml
# Aggiunta variabili d'ambiente
sed -i '/DEBUG=true/ a\      - USE_MOCK_ELASTICSEARCH=true\n      - USE_SIMPLE_CHATBOT=true' docker-compose.yml
echo "Docker Compose aggiornato."

# 4. Eliminazione volume Elasticsearch
echo "Rimozione volumi Elasticsearch..."
docker volume rm $(docker volume ls -q | grep elasticsearch) || true
echo "Volumi Elasticsearch rimossi."

# 5. Applicazione migrazioni database
echo "Applicazione migrazioni database..."
# Assicuriamoci che i container siano in esecuzione
docker-compose up -d db
# Esegui migrazioni
docker-compose exec api alembic upgrade head
echo "Migrazioni database applicate."

# 6. Riavvio contenitore API con nuove configurazioni
echo "Riavvio contenitore API..."
docker-compose up -d --build api
echo "Contenitore API riavviato con nuove configurazioni."

echo
echo "=== Modifiche applicate con successo! ==="
echo "Il sistema Compliance Compass ora funziona senza Elasticsearch e Chatbot."
echo "Il servizio di ricerca utilizza SQL e il chatbot è stato sostituito con FAQ."
echo
echo "Per verificare il funzionamento:"
echo "- API: http://localhost:8000/api/health"
echo "- Documentazione API: http://localhost:8000/api/docs"
echo