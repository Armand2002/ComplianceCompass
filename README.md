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
- 4GB RAM minimo (8GB raccomandati)
- 20GB di spazio disco disponibile

### Ambiente di Sviluppo

1. **Clona il repository**
   ```bash
   git clone https://github.com/username/compliance-compass.git
   cd compliance-compass
   ```

2. **Crea il file di configurazione ambientale**
   ```bash
   cp .env.example .env
   ```

3. **Personalizza la configurazione (opzionale)**
   
   Modifica il file `.env` per configurare:
   - Credenziali database
   - Chiavi JWT
   - Parametri di connessione Elasticsearch
   - Configurazione email

4. **Avvio Rapido**

   Utilizza lo script automatico per Windows:
   ```bash
   run.bat
   ```

   Oppure, per Linux/Mac:
   ```bash
   chmod +x run.sh
   ./run.sh
   ```

5. **Avvio Manuale**
   ```bash
   docker-compose build
   docker-compose up -d
   ```

6. **Verifica lo stato dei servizi**
   ```bash
   docker-compose ps
   ```

7. **Popola il database con dati iniziali**
   ```bash
   docker-compose exec api python -m scripts.seed_db
   ```

8. **Accedi all'applicazione**
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - Documentazione API: http://localhost:8000/api/docs

### Ambiente di Produzione

1. **Clona e configura**
   ```bash
   git clone https://github.com/username/compliance-compass.git
   cd compliance-compass
   cp .env.example .env.prod
   ```

2. **Configura le impostazioni di produzione**
   
   Modifica `.env.prod` per impostare:
   - `ENVIRONMENT=production`
   - `DEBUG=False`
   - Credenziali sicure per database e servizi
   - URL frontend definitivo
   - Configurazione SMTP valida

3. **Prepara i certificati TLS (solo produzione)**
   ```bash
   mkdir -p docker/nginx/certs
   # Copia i tuoi certificati o configura Let's Encrypt
   ```

4. **Costruisci e avvia i container di produzione**
   ```bash
   docker-compose -f docker-compose-prod.yml --env-file .env.prod up -d
   ```

5. **Verifica il funzionamento**
   ```bash
   docker-compose -f docker-compose-prod.yml logs -f
   ```

6. Configura il tuo server DNS per puntare al tuo server e aggiorna la configurazione NGINX nel file `docker/nginx/nginx.conf`.

## 🔧 Comandi Utili

### Gestione Container

```bash
# Ferma i container
docker-compose down

# Riavvia un servizio specifico
docker-compose restart api

# Visualizza logs in tempo reale
docker-compose logs -f
```

### Manutenzione Database

```bash
# Accedi al database PostgreSQL
docker-compose exec db psql -U postgres -d compliance_compass

# Esegui migrazione del database
docker-compose exec api alembic upgrade head

# Backup del database
docker-compose exec db pg_dump -U postgres compliance_compass > backup.sql
```

### Indicizzazione Elasticsearch

```bash
# Ricostruisci gli indici
curl -X POST http://localhost:8000/api/search/reindex

# Verifica stato Elasticsearch
curl http://localhost:9200/_cluster/health
```

## 🔍 Troubleshooting

### Problema: I container non si avviano

1. Verifica che le porte non siano in uso:
   ```bash
   netstat -tuln | grep '5432\|8000\|3000\|9200'
   ```

2. Controlla i log di errore:
   ```bash
   docker-compose logs api
   ```

### Problema: Elasticsearch non si connette

1. Verifica che Elasticsearch sia in esecuzione:
   ```bash
   docker-compose ps elasticsearch
   ```

2. Inizializza manualmente gli indici:
   ```bash
   curl -X POST http://localhost:8000/api/admin/elasticsearch/setup
   ```

### Problema: Dati mancanti

Esegui lo script di seeding con opzioni specifiche:
```bash
docker-compose exec api python -m scripts.seed_db --admin-only
```

### Test dopo l'installazione

Verifica che tutto funzioni correttamente:

```bash
# Test dell'API
curl http://localhost:8000/api/health

# Test di login (sostituisci con credenziali reali)
curl -X POST http://localhost:8000/api/auth/login -H "Content-Type: application/json" -d '{"username":"admin", "password":"admin123"}'
```

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

## 📝 Architettura di Sistema

### Componenti Principali

- **Backend**: FastAPI con architettura MVC
- **Database**: PostgreSQL con ORM SQLAlchemy
- **Indicizzazione**: Elasticsearch per ricerca avanzata
- **Autenticazione**: JWT con gestione ruoli e permessi
- **Caching**: Sistema di caching avanzato per ottimizzazione delle prestazioni

### Principali Funzionalità

- Gestione centralizzata dei Privacy Patterns
- Ricerca semantica avanzata
- Supporto multi-lingue
- Integrazione con standard GDPR e Privacy by Design
- Chatbot intelligente per assistenza

## 🔒 Sicurezza

- Autenticazione basata su JWT
- Protezione contro attacchi brute-force
- Gestione granulare dei permessi
- Crittografia delle password
- Middleware di sicurezza personalizzati
- Gestione dei rate limit

## 📄 Licenza

Questo progetto è distribuito sotto licenza MIT. Vedi il file `LICENSE` per maggiori dettagli.

## 📧 Contatti

Per supporto, bug o suggerimenti:
- Email: support@compliancecompass.com
- GitHub Issues: [Link al repository]

**Nota**: Questo progetto è in fase di sviluppo. Le funzionalità e l'architettura sono soggette a modifiche.