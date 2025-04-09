Piano di Sviluppo Completo per ComplianceCompass
Ho analizzato a fondo il tuo codebase e ho elaborato un piano di sviluppo completo per risolvere definitivamente tutti i problemi relativi agli errori 500 nelle API e ai problemi di rendering dei componenti React.

Problema Principale
Il problema centrale è il disallineamento tra i modelli SQLAlchemy e lo schema del database, in particolare:

La colonna view_count definita nel modello PrivacyPattern ma non esistente nella tabella privacy_patterns
Caricamento non ottimizzato delle relazioni nei modelli
Problemi di resilienza nelle API
Piano di Sviluppo in 5 Fasi


Fase 1: Allineamento del Database (Giorno 1)
1.1. Generazione di una migrazione unificata
"""Script per generare una migrazione unificata che risolve tutti i problemi di schema."""
import alembic.config
import sys
import os

def main():
    # Aggiungi la directory root al path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    
    # Configura alembic
    alembic_args = [
        '--raiseerr',
        'revision',
        '--autogenerate',
        '-m', "align_models_with_database"
    ]
    
    # Esegui comando alembic
    alembic.config.main(argv=alembic_args)

if __name__ == "__main__":
    main()

1.2. Script di applicazione sicura della migrazione
"""Script per applicare le migrazioni in modo sicuro."""
import alembic.config
import sys
import os
import subprocess

def backup_database():
    """Crea un backup del database prima della migrazione."""
    result = subprocess.run(
        ["pg_dump", "-h", "db", "-U", "postgres", "-d", "compliance_compass", "-f", "/tmp/backup_before_migration.sql"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"Errore nel backup del database: {result.stderr}")
        return False
    return True

def main():
    # Aggiungi la directory root al path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    
    # Backup database
    if not backup_database():
        print("Impossibile procedere senza backup")
        return
        
    # Applica migrazioni
    alembic_args = [
        '--raiseerr',
        'upgrade', 
        'head'
    ]
    
    # Esegui comando alembic
    try:
        alembic.config.main(argv=alembic_args)
        print("Migrazione applicata con successo!")
    except Exception as e:
        print(f"Errore durante la migrazione: {str(e)}")
        print("Consultare il backup in /tmp/backup_before_migration.sql")

if __name__ == "__main__":
    main()
    
1.3. Verificare ed eseguire la migrazione
# Generazione della migrazione
docker-compose exec api python -m scripts.create_migration

# Verifica della migrazione generata
docker-compose exec api alembic history -v

# Applicazione della migrazione
docker-compose exec api python -m scripts.apply_migration


Fase 2: Ottimizzazione dei Modelli (Giorno 2)

2.1. Revisione e standardizzazione del modello GDPRArticle
# Parte del file che richiede modifica
class GDPRArticle(Base):
    # Altri campi...
    
    # Miglioramento: strategia di caricamento consistente
    patterns = relationship(
        "PrivacyPattern", 
        secondary=pattern_gdpr_association, 
        back_populates="gdpr_articles", 
        lazy="selectin"  # Cambiato da "noload" a "selectin" per ottimizzare le query
    )
    
    # Metodo to_dict migliorato
    def to_dict(self):
        """Converte l'oggetto in un dizionario in modo sicuro."""
        result = {
            "id": self.id,
            "number": self.number,
            "title": self.title,
            "content": self.content,
            "summary": self.summary,
            "category": self.category,
            "chapter": self.chapter,
            "is_key_article": self.is_key_article,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        
        # Aggiungi relazioni solo se caricate (evita eccezioni)
        if 'patterns' in self.__dict__:
            result["patterns"] = [
                {"id": p.id, "title": p.title} for p in self.patterns
            ]
            
        return result

2.2. Revisione del modello PrivacyPattern
class PrivacyPattern(Base):
    # Altri campi...
    
    # Assicurati che view_count sia definito correttamente
    view_count = Column(Integer, nullable=True, default=0)
    
    # Strategia di caricamento consistente
    gdpr_articles = relationship(
        "GDPRArticle", 
        secondary=pattern_gdpr_association, 
        back_populates="patterns",
        lazy="selectin"  # Strategia di caricamento ottimizzata
    )
    
    # Metodo to_dict migliorato con gestione sicura delle relazioni
    def to_dict(self):
        """Converte l'oggetto in un dizionario in modo sicuro."""
        result = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "context": self.context,
            "problem": self.problem,
            "solution": self.solution,
            "consequences": self.consequences,
            "strategy": self.strategy,
            "mvc_component": self.mvc_component,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by_id": getattr(self, "created_by_id", None),
            "view_count": getattr(self, "view_count", 0),
        }
        
        # Aggiunta sicura delle relazioni solo se caricate
        if 'gdpr_articles' in self.__dict__ and self.gdpr_articles:
            result["gdpr_articles"] = [
                {"id": g.id, "number": g.number, "title": g.title} 
                for g in self.gdpr_articles
            ]
        else:
            result["gdpr_articles"] = []
            
        # Altre relazioni...
        
        return result


Fase 3: Implementazione del Service Layer (Giorno 3)
3.1. Creazione di servizi centralizzati
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging
from src.models.gdpr_model import GDPRArticle
from src.utils.cache import Cache

# Configurazione del logger
logger = logging.getLogger(__name__)

# Istanza di cache centralizzata
cache = Cache()

class GDPRService:
    """
    Servizio centralizzato per operazioni relative agli articoli GDPR.
    Implementa pattern di resilienza e caching.
    """
    
    @staticmethod
    @cache.cached(ttl=300)  # Cache per 5 minuti
    def get_articles(db: Session, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Recupera articoli GDPR con gestione degli errori e caching.
        """
        try:
            articles = db.query(GDPRArticle).order_by(GDPRArticle.number).offset(skip).limit(limit).all()
            return [article.to_dict() for article in articles]
        except SQLAlchemyError as e:
            logger.error(f"Database error in get_articles: {str(e)}")
            # Implementazione circuit breaker: ritorna dati vuoti in caso di errore
            return []
        except Exception as e:
            logger.error(f"Unexpected error in get_articles: {str(e)}")
            return []
    
    @staticmethod
    @cache.cached(ttl=300)
    def get_article(db: Session, article_id: int) -> Optional[Dict[str, Any]]:
        """
        Recupera un articolo specifico per ID con gestione degli errori.
        """
        try:
            article = db.query(GDPRArticle).filter(GDPRArticle.id == article_id).first()
            return article.to_dict() if article else None
        except Exception as e:
            logger.error(f"Error retrieving article {article_id}: {str(e)}")
            return None

3.2. Implementazione dell'utilità di cache
from functools import wraps
import time
from typing import Dict, Any, Callable, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class Cache:
    """
    Implementazione di un sistema di caching in-memory con TTL.
    """
    def __init__(self):
        self._cache: Dict[str, Tuple[Any, float]] = {}
    
    def cached(self, ttl: int = 60):
        """
        Decorator per cachare i risultati delle funzioni.
        
        Args:
            ttl: Tempo di vita in secondi per la cache
        """
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Crea una chiave unica basata su funzione e parametri
                key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
                
                # Verifica se il valore è in cache e non è scaduto
                if key in self._cache:
                    value, timestamp = self._cache[key]
                    if time.time() - timestamp < ttl:
                        logger.debug(f"Cache hit for {key}")
                        return value
                
                # Esegui la funzione e salva il risultato in cache
                logger.debug(f"Cache miss for {key}")
                result = func(*args, **kwargs)
                self._cache[key] = (result, time.time())
                return result
                
            return wrapper
        return decorator
    
    def clear(self, pattern: Optional[str] = None):
        """
        Pulisce la cache, opzionalmente solo le chiavi che corrispondono a un pattern.
        """
        if pattern:
            self._cache = {k: v for k, v in self._cache.items() if pattern not in k}
        else:
            self._cache.clear()


Fase 4: Miglioramento delle API (Giorno 4-5)
4.1. Controller base con gestione degli errori standardizzata
from typing import List, Dict, Any, TypeVar, Generic, Type
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

# Configurazione del logger
logger = logging.getLogger(__name__)

T = TypeVar('T')

class BaseController(Generic[T]):
    """
    Controller base con implementazione standard delle operazioni CRUD
    e gestione centralizzata degli errori.
    """
    
    model_class: Type[T] = None
    
    @classmethod
    def get_all(cls, db: Session, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Recupera una lista paginata di record con gestione degli errori."""
        try:
            items = db.query(cls.model_class).offset(skip).limit(limit).all()
            return [item.to_dict() for item in items]
        except SQLAlchemyError as e:
            logger.error(f"Database error in {cls.__name__}.get_all: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in {cls.__name__}.get_all: {str(e)}")
            return []

4.2. Controller GDPR migliorato
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func
import logging

from src.models.gdpr_model import GDPRArticle
from src.controllers.base_controller import BaseController
from src.services.gdpr_service import GDPRService

# Configurazione del logger
logger = logging.getLogger(__name__)

class GDPRController(BaseController[GDPRArticle]):
    """
    Controller per la gestione degli articoli GDPR.
    """
    model_class = GDPRArticle
    
    @staticmethod
    def get_articles(db: Session, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Recupera una lista paginata di articoli GDPR, delegando al service.
        """
        return GDPRService.get_articles(db, skip, limit)
    
    # Altri metodi migliorati...

4.3. Rotte GDPR con risposta standardizzata
# Mantenere il codice esistente ma aggiungere:

from src.utils.response_formatter import format_response

@router.get(
    "/api/gdpr/articles",
    summary="Lista articoli GDPR", 
    response_description="Lista paginata di articoli GDPR"
)
def get_gdpr_articles(
    response: Response,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Recupera una lista paginata di articoli GDPR con risposta standardizzata."""
    try:
        result = GDPRController.get_articles(db, skip=skip, limit=limit)
        
        # Formatta la risposta in modo standard
        return format_response(
            data={
                "items": result,
                "total": len(result),
                "page": skip // limit + 1 if limit > 0 else 1,
                "pages": (len(result) + limit - 1) // limit if limit > 0 else 1
            }
        )
    except Exception as e:
        logger.error(f"Error in get_gdpr_articles: {str(e)}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return format_response(error=str(e))

4.4. Utilità di formattazione della risposta
from typing import Dict, Any, Optional

def format_response(
    data: Any = None,
    error: Optional[str] = None,
    message: str = "Success"
) -> Dict[str, Any]:
    """
    Formatta le risposte API in modo coerente.
    
    Args:
        data: Dati da restituire
        error: Eventuale messaggio di errore
        message: Messaggio di successo
        
    Returns:
        Risposta API formattata
    """
    response = {
        "status": "error" if error else "success",
        "message": error if error else message
    }
    
    if data is not None:
        response["data"] = data
        
    return response


Fase 5: Frontend resiliente (Giorno 6-7)
5.1. Configurazione del servizio API centralizzato
import axios from 'axios';
import { toast } from 'react-toastify';

// Istanza axios centralizzata
const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor per le richieste
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Interceptor per le risposte
api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    console.error('API Error:', error);
    
    // Gestione comune degli errori
    if (error.response) {
      // Gestione errori 401 (già implementata in axios.js)
      if (error.response.status === 401) {
        // ...codice esistente per token refresh
      }
      
      // Gestione errori 500
      else if (error.response.status === 500) {
        toast.error('Si è verificato un errore nel server. Riprova più tardi.');
        
        // Logging avanzato per il debug
        console.error('Server error details:', error.response.data);
      }
    } else if (error.request) {
      // La richiesta è stata fatta ma non c'è stata risposta
      toast.error('Impossibile contattare il server.');
    } else {
      // Errori nella configurazione della richiesta
      toast.error('Si è verificato un errore nella richiesta.');
    }
    
    return Promise.reject(error);
  }
);

export default api;

5.2. Servizio GDPR con resilienza
import api from './api';

const GDPRService = {
  /**
   * Recupera tutti gli articoli GDPR con gestione degli errori
   * @param {Object} params - Parametri di paginazione
   * @returns {Promise} - Promise con i dati di risposta o dati vuoti in caso di errore
   */
  getArticles: async (params = {}) => {
    try {
      const response = await api.get('/gdpr/articles', { params });
      return response.data.data || { items: [], total: 0 };
    } catch (error) {
      console.error('Error fetching GDPR articles:', error);
      // Ritorna dati vuoti in caso di errore per evitare errori a cascata
      return { items: [], total: 0 };
    }
  },
  
  /**
   * Recupera un articolo specifico per numero
   * @param {string} number - Numero dell'articolo
   * @returns {Promise} - Promise con i dati dell'articolo
   */
  getArticleByNumber: async (number) => {
    try {
      const response = await api.get(`/gdpr/articles/number/${number}`);
      return response.data.data;
    } catch (error) {
      console.error(`Error fetching GDPR article ${number}:`, error);
      throw error;
    }
  }
};

export default GDPRService;
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import GDPRService from '../../services/gdprService';
import './GDPRPage.scss';

const GDPRPage = () => {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchArticles = async () => {
      try {
        setLoading(true);
        // Usa il servizio centralizzato invece di axios direttamente
        const data = await GDPRService.getArticles();
        setArticles(data.items || []);
        setError(null);
      } catch (err) {
        console.error('Errore nel caricamento degli articoli GDPR:', err);
        setError('Impossibile caricare gli articoli GDPR. Riprova più tardi.');
      } finally {
        setLoading(false);
      }
    };

    fetchArticles();
  }, []);

  // Resto del componente invariato...
};

export default GDPRPage;

5.3. Componente GDPR migliorato
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import GDPRService from '../../services/gdprService';
import './GDPRPage.scss';

const GDPRPage = () => {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchArticles = async () => {
      try {
        setLoading(true);
        // Usa il servizio centralizzato invece di axios direttamente
        const data = await GDPRService.getArticles();
        setArticles(data.items || []);
        setError(null);
      } catch (err) {
        console.error('Errore nel caricamento degli articoli GDPR:', err);
        setError('Impossibile caricare gli articoli GDPR. Riprova più tardi.');
      } finally {
        setLoading(false);
      }
    };

    fetchArticles();
  }, []);

  // Resto del componente invariato...
};

export default GDPRPage;

Fase 6: Monitoraggio e Manutenzione (Giorno 8-10)
6.1. Endpoint di health centralizzato
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
import psutil
import time
import os

from src.db.session import get_db

router = APIRouter(prefix="/monitoring", tags=["monitoraggio"])

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    Verifica completa dello stato del sistema.
    """
    start_time = time.time()
    result = {
        "status": "healthy",
        "timestamp": time.time(),
        "components": {}
    }
    
    # Verifica database
    try:
        db.execute(text("SELECT 1"))
        result["components"]["database"] = {
            "status": "healthy",
            "latency_ms": round((time.time() - start_time) * 1000, 2)
        }
    except Exception as e:
        result["status"] = "degraded"
        result["components"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # Verifica filesystem
    try:
        disk = psutil.disk_usage(os.path.abspath(os.sep))
        result["components"]["filesystem"] = {
            "status": "healthy",
            "usage_percent": disk.percent,
            "free_gb": round(disk.free / (1024 ** 3), 2)
        }
        
        if disk.percent > 90:
            result["components"]["filesystem"]["status"] = "warning"
            if result["status"] == "healthy":
                result["status"] = "warning"
    except Exception as e:
        result["components"]["filesystem"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Metriche di sistema
    result["system"] = {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "response_time_ms": round((time.time() - start_time) * 1000, 2)
    }
    
    return result

6.2. Script di verifica integrità database
"""
Script per verificare l'integrità del database e correggere eventuali problemi.
"""
import sys
import os
import traceback
from sqlalchemy import MetaData, inspect, text

# Aggiungi la directory root al sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.db.session import SessionLocal, engine
from src.models.gdpr_model import GDPRArticle
from src.models.privacy_pattern import PrivacyPattern

def check_table_exists(inspector, table_name):
    """Verifica se una tabella esiste."""
    return table_name in inspector.get_table_names()

def check_column_exists(inspector, table_name, column_name):
    """Verifica se una colonna esiste in una tabella."""
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def main():
    try:
        db = SessionLocal()
        inspector = inspect(engine)
        
        print("=== Verifica integrità database ===")
        
        # Verifica tabelle principali
        for table_name in ["gdpr_articles", "privacy_patterns", "users"]:
            exists = check_table_exists(inspector, table_name)
            print(f"Tabella {table_name}: {'OK' if exists else 'MANCANTE'}")
            
        # Verifica colonna view_count in privacy_patterns
        if check_table_exists(inspector, "privacy_patterns"):
            has_view_count = check_column_exists(inspector, "privacy_patterns", "view_count")
            print(f"Colonna view_count in privacy_patterns: {'OK' if has_view_count else 'MANCANTE'}")
            
            # Aggiungi colonna se mancante
            if not has_view_count:
                print("Aggiunta della colonna view_count...")
                db.execute(text("ALTER TABLE privacy_patterns ADD COLUMN view_count INTEGER DEFAULT 0"))
                db.commit()
                print("Colonna view_count aggiunta correttamente.")
        
        # Verifica record nelle tabelle principali
        gdpr_count = db.query(GDPRArticle).count()
        pattern_count = db.query(PrivacyPattern).count()
        
        print(f"Articoli GDPR nel database: {gdpr_count}")
        print(f"Privacy Patterns nel database: {pattern_count}")
        
        print("\n=== Verifica completata ===")
        
    except Exception as e:
        print(f"Errore durante la verifica: {str(e)}")
        traceback.print_exc()
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    main()

6.3. Aggiornamento del script di startup
# Aggiungi all'avvio dell'applicazione

@app.on_event("startup")
async def startup_checks():
    """Esegue controlli all'avvio dell'applicazione."""
    try:
        # Verifica connessione DB
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
            logger.info("Database connection: OK")
        
        # Registro i router per il monitoraggio
        from src.routes import monitoring_routes
        app.include_router(monitoring_routes.router, prefix="/api")
        
        logger.info("Application startup checks completed successfully.")
    except Exception as e:
        logger.error(f"Startup check failed: {str(e)}")
        
Sequenza di Implementazione
Giorni 1-2: Allineamento del database e ottimizzazione modelli

Generare migrazione per view_count
Ottimizzare le relazioni nei modelli
Implementare metodi to_dict più robusti
Giorni 3-4: Service layer e base controller

Implementare il service pattern per la logica di business
Creare un controller base con gestione errori standardizzata
Aggiungere caching e resilienza
Giorni 5-6: Miglioramento API e frontend

Aggiornare le rotte con risposte standardizzate
Implementare servizi centralizzati nel frontend
Migliorare la gestione degli errori nelle API
Giorni 7-8: Testing e validazione

Testare tutte le API con vari scenari di errore
Verificare la resilienza del frontend
Testare l'integrazione end-to-end
Giorni 9-10: Monitoraggio e documentazione

Implementare endpoint di health check
Aggiungere script di verifica dell'integrità del database
Documentare l'architettura e le best practice
Vantaggi della Soluzione
Risoluzione permanente dei problemi di disallineamento tra modelli e schema database
Resilienza a livello di API e frontend contro errori futuri
Performance migliorata attraverso strategie di caching e caricamento ottimizzate
Manutenibilità grazie alla standardizzazione dei pattern
Monitoraggio proattivo per identificare problemi prima che causino errori visibili agli utenti
Questo piano di sviluppo affronta non solo i sintomi (errori 500) ma anche le cause radice, garantendo una soluzione duratura che migliorerà la stabilità e le prestazioni dell'intera applicazione ComplianceCompass.