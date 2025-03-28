# Compliance Compass

Piattaforma wiki collaborativa per semplificare la comprensione delle normative tecniche e di sicurezza.

## 📋 Funzionalità Principali

- **Repository centralizzato di normative**: Accesso unificato a GDPR, Privacy by Design e standard di sicurezza.
- **Chatbot intelligente**: Assistente basato su NLP per risposte e suggerimenti.
- **Ricerca avanzata**: Sistema di ricerca semantico con filtri multidimensionali.
- **Privacy Pattern**: Collezione di soluzioni pratiche per implementare la privacy nei sistemi.
- **Interfaccia moderna**: Design responsive e accessibile.

## 🛠 Tecnologie

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL
- **Search Engine**: Elasticsearch
- **Frontend**: React.js
- **Containerization**: Docker

## 🚀 Installazione e Avvio

### Prerequisiti

- Docker e Docker Compose
- Git

### Setup Sviluppo

1. Clona il repository:
   ```bash
   git clone https://github.com/username/compliance-compass.git
   cd compliance-compass
   ```

2. Crea il file `.env` basandoti su `.env.example`:
   ```bash
   cp .env.example .env
   ```

3. Configura le variabili d'ambiente nel file `.env` secondo le tue necessità.

4. Avvia i container di sviluppo:
   ```bash
   docker-compose up -d
   ```

5. L'API sarà disponibile su: http://localhost:8000
   Documentazione API: http://localhost:8000/api/docs
   Frontend: http://localhost:3000

### Setup Produzione

1. Configura le variabili d'ambiente:
   ```bash
   cp .env.example .env.prod
   ```

2. Modifica il file `.env.prod` con le configurazioni di produzione.

3. Avvia con Docker Compose per produzione:
   ```bash
   docker-compose -f docker/docker-compose.prod.yml --env-file .env.prod up -d
   ```

4. Configura il tuo server DNS per puntare al tuo server e aggiorna la configurazione NGINX nel file `docker/nginx/nginx.conf`.

## 📊 Struttura del Progetto

```
compliance-compass/
├── src/                       # Codice sorgente backend
│   ├── controllers/           # Logica di business
│   ├── models/                # Modelli dati
│   ├── routes/                # API endpoints
│   ├── schemas/               # Schemi Pydantic
│   ├── services/              # Servizi esterni
│   └── utils/                 # Funzioni di utilità
├── frontend/                  # Codice sorgente frontend React
├── alembic/                   # Migrazioni database
├── scripts/                   # Script di utility
├── tests/                     # Test unitari e d'integrazione
└── docker/                    # Configurazione Docker
```

## 🧪 Testing

Esegui i test unitari e d'integrazione:

```bash
# Test backend
pytest

# Con coverage
pytest --cov=src tests/
```

## 📚 API Documentation

La documentazione API è disponibile all'indirizzo `/api/docs` in formato Swagger UI o `/api/redoc` in formato Redoc.

## 📦 Seed Data

Per popolare il database con dati iniziali:

```bash
docker-compose exec api python -m scripts.seed_db
```

## 🔍 Configurazione Elasticsearch

Elasticsearch è utilizzato per la ricerca avanzata. Per reindicizzare tutti i pattern:

```bash
curl -X POST http://localhost:8000/api/search/reindex
```

## 👥 Contribuire

1. Fork il repository
2. Crea un branch: `git checkout -b feature-nome`
3. Committa le modifiche: `git commit -m 'Aggiungi nuova feature'`
4. Push al branch: `git push origin feature-nome`
5. Apri una Pull Request

## 📄 Licenza

Questo progetto è distribuito sotto licenza MIT. Vedi il file `LICENSE` per maggiori dettagli.