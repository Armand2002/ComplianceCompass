Piano di Sviluppo per la Rimozione di Elasticsearch e Chatbot
Comprendo che stai riscontrando problemi con Elasticsearch e il chatbot che impediscono il corretto funzionamento del tuo progetto Compliance Compass. Ti propongo un piano strutturato per rimuovere questi componenti problematici mantenendo le funzionalità principali dell'applicazione.
1. Analisi dell'Impatto
Componenti da rimuovere:

Elasticsearch: utilizzato per la ricerca avanzata e l'indicizzazione dei pattern
Chatbot: fornisce assistenza agli utenti

Funzionalità da mantenere/sostituire:

La ricerca di base e avanzata (sostituendo Elasticsearch con query SQL)
Un'interfaccia di supporto semplificata (alternative al chatbot)

2. Piano di Rimozione di Elasticsearch
2.1 Modifiche al Codice

Implementare una soluzione di ricerca basata su SQL:
pythonCopia# src/services/search_service.py
# Sostituire la classe SearchService con una versione che usa solo SQL

class SearchService:
    """Servizio di ricerca basato su SQL invece di Elasticsearch."""
    
    def __init__(self):
        self.es = None  # Mantenuto per compatibilità, ma non usato
    
    def search_patterns(self, query=None, strategy=None, mvc_component=None, 
                       gdpr_id=None, pbd_id=None, iso_id=None, 
                       vulnerability_id=None, from_pos=0, size=10):
        """Implementazione di ricerca basata su SQL."""
        # Implementare qui la logica di ricerca con SQLAlchemy
        return self._db_search_fallback(query, strategy, mvc_component, 
                                        gdpr_id, pbd_id, iso_id, 
                                        vulnerability_id, from_pos, size)
    
    def _db_search_fallback(self, query, strategy, mvc_component, 
                           gdpr_id, pbd_id, iso_id, vulnerability_id, 
                           from_pos, size):
        """Ricerca pattern nel database usando SQLAlchemy."""
        # Implementazione

Eliminare dipendenze da Elasticsearch:

Rimuovere elasticsearch da requirements.txt
Commentare o rimuovere l'inizializzazione di Elasticsearch in src/main.py


Disabilitare servizi correlati:

Rimuovere il servizio Elasticsearch da docker-compose.yml



2.2 Ottimizzare Query SQL

Creare indici SQL efficaci:
sqlCopia-- Da eseguire come migrazione
CREATE INDEX idx_privacy_patterns_title_description ON privacy_patterns (title, description);
CREATE INDEX idx_privacy_patterns_strategy ON privacy_patterns (strategy);
CREATE INDEX idx_privacy_patterns_mvc_component ON privacy_patterns (mvc_component);

Implementare ricerca full-text con PostgreSQL:
pythonCopia# Esempio di query full-text con PostgreSQL
query = db.query(PrivacyPattern).filter(
    or_(
        PrivacyPattern.title.ilike(f"%{search_term}%"),
        PrivacyPattern.description.ilike(f"%{search_term}%"),
        PrivacyPattern.context.ilike(f"%{search_term}%"),
        # Altri campi rilevanti
    )
)


3. Piano di Rimozione del Chatbot
3.1 Rimuovere Codice Chatbot

Eliminare moduli relativi al chatbot:

Rimuovere o disabilitare src/services/chatbot_service.py
Disabilitare gli endpoint relativi in src/routes/chatbot_routes.py


Aggiornare le dipendenze:

Rimuovere dipendenze NLP da requirements.txt:
Copia# Rimuovere:
nltk==3.8.1
scikit-learn==1.3.0
sentence-transformers==2.2.2




3.2 Implementare Alternativa Semplice

Sostituire con una pagina FAQ statica:
pythonCopia# src/routes/faq_routes.py
@router.get("/faq", response_model=List[Dict[str, str]])
async def get_faq():
    """Restituisce una lista di FAQ preconfigurate."""
    return [
        {"question": "Come cercare un pattern?", 
         "answer": "Utilizza la barra di ricerca in alto inserendo parole chiave"},
        {"question": "Cos'è un Privacy Pattern?",
         "answer": "Un Privacy Pattern è una soluzione riutilizzabile..."},
        # Altre FAQ
    ]


4. Modifiche alla Configurazione
4.1 Aggiornare File di Configurazione

Modificare .env e .env.example:
Copia# Modificare o rimuovere variabili Elasticsearch
# ELASTICSEARCH_URL=http://elasticsearch:9200
# Impostare USE_MOCK_ELASTICSEARCH a true
USE_MOCK_ELASTICSEARCH=true

# Modificare o rimuovere variabili Chatbot
# AI_API_KEY=your_openai_api_key
USE_SIMPLE_CHATBOT=true


4.2 Modificare Docker Compose

Rimuovere servizio Elasticsearch:
yamlCopia# docker-compose.yml
# Rimuovere o commentare:
# elasticsearch:
#   image: elasticsearch:7.17.7
#   environment:
#     - discovery.type=single-node
#     - ES_JAVA_OPTS=-Xms512m -Xmx512m
#   ports:
#     - "9200:9200"


5. Fasi di Implementazione
Fase 1: Preparazione (1 giorno)

Backup del database e del codice attuale
Creazione di un branch git separato per le modifiche

Fase 2: Rimozione di Elasticsearch (1-2 giorni)

Implementare ricerca basata su database SQL
Creare indici necessari per ottimizzare le query
Rimuovere dipendenze da Elasticsearch
Testare le nuove funzionalità di ricerca

Fase 3: Sostituzione del Chatbot (1 giorno)

Rimuovere il codice del chatbot
Implementare l'alternativa scelta (FAQ)
Aggiornare l'interfaccia utente

Fase 4: Test e Ottimizzazione (1-2 giorni)

Test completo dell'applicazione
Ottimizzazione delle query per migliorare le prestazioni
Correzione di eventuali bug

Fase 5: Deployment (1 giorno)

Aggiornare il file docker-compose
Ricostruire e avviare i container
Verificare il corretto funzionamento nell'ambiente di produzione

6. Considerazioni finali
Vantaggi della rimozione

Riduzione della complessità dell'infrastruttura
Minori requisiti di risorse hardware
Eliminazione delle dipendenze problematiche
Maggiore stabilità del sistema

Limitazioni

Ricerca meno sofisticata senza Elasticsearch (ma funzionale)
Supporto utente meno interattivo senza chatbot

Questo piano ti permetterà di eliminare i componenti problematici mantenendo l'applicazione funzionale. La ricerca basata su SQL sarà meno potente di Elasticsearch, ma sufficiente per molti casi d'uso, e una sezione FAQ ben strutturata può sostituire efficacemente un chatbot semplice.