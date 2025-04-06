# src/logging_config.py
"""
Configurazione centralizzata del logging per l'applicazione.

Fornisce una configurazione standardizzata per la registrazione 
dei log con formattazione e gestione dei livelli.
"""

import logging
import os
import sys
import json
import time
import traceback
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from typing import Optional, Dict, Any, Callable, List, Union

class ContextAdapter(logging.LoggerAdapter):
    """
    Adapter che aggiunge contesto ai messaggi di log.
    
    Permette di arricchire i log con metadati come request_id, user_id, ecc.
    """
    def process(self, msg, kwargs):
        # Aggiungi contesto al messaggio
        return msg, kwargs

class JSONFormatter(logging.Formatter):
    """
    Formatter che produce log in formato JSON.
    
    Utile per consumare i log con strumenti di analisi log.
    """
    def __init__(self, include_stack_info=False):
        super().__init__()
        self.include_stack_info = include_stack_info
        
    def format(self, record):
        log_record = {
            'timestamp': self.formatTime(record, datefmt='%Y-%m-%dT%H:%M:%S.%fZ'),
            'level': record.levelname,
            'logger': record.name,
            'thread': record.thread,
            'message': record.getMessage()
        }
        
        # Includi altri attributi dalla traccia della richiesta
        for attr in ['request_id', 'user_id', 'ip', 'path', 'method']:
            if hasattr(record, attr):
                log_record[attr] = getattr(record, attr)
        
        # Aggiungi info sullo stack per gli errori
        if self.include_stack_info and record.exc_info:
            log_record['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
        elif record.exc_text:
            log_record['exception'] = record.exc_text
            
        return json.dumps(log_record)

def get_request_context_filter():
    """
    Crea un filtro per includere informazioni sulla richiesta nei log.
    
    Utilizzato per arricchire i log con informazioni dal contesto 
    della richiesta FastAPI.
    """
    class RequestContextFilter(logging.Filter):
        request_context = {}
        
        def filter(self, record):
            for key, value in self.request_context.items():
                setattr(record, key, value)
            return True
    
    return RequestContextFilter()

request_context_filter = get_request_context_filter()

def configure_logging(
    log_level: str = 'INFO', 
    log_dir: Optional[str] = None,
    environment: str = 'development',
    service_name: str = 'compliance-compass'
) -> None:
    """
    Configura il sistema di logging per l'applicazione.
    
    Args:
        log_level (str, optional): Livello di logging. Defaults a 'INFO'.
        log_dir (str, optional): Directory per i file di log. Se None, usa './logs'.
        environment (str): Ambiente di esecuzione (development, staging, production)
        service_name (str): Nome del servizio per i log
    """
    # Determina la directory dei log
    log_directory = log_dir or os.path.join(os.getcwd(), 'logs')
    
    # Crea la directory dei log se non esiste
    os.makedirs(log_directory, exist_ok=True)
    
    # Livello di log numerico
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {log_level}')
    
    # Resetta le configurazioni esistenti
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Configura il logger root
    root_logger.setLevel(numeric_level)
    
    # Configurazione handler console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    
    # Scegli il formatter in base all'ambiente
    if environment == 'production':
        formatter = JSONFormatter(include_stack_info=True)
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - '
            '%(request_id)s - %(user_id)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Aggiungi il filtro di contesto
    console_handler.addFilter(request_context_filter)
    
    # Configurazione file handler con rotazione
    if environment in ('production', 'staging'):
        # In produzione/staging usa rotazione giornaliera
        file_handler = TimedRotatingFileHandler(
            filename=os.path.join(log_directory, f'{service_name}.log'),
            when='midnight',
            backupCount=14  # 2 settimane
        )
    else:
        # In development usa rotazione per dimensione
        file_handler = RotatingFileHandler(
            filename=os.path.join(log_directory, f'{service_name}.log'),
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5
        )
    
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(formatter)
    file_handler.addFilter(request_context_filter)
    root_logger.addHandler(file_handler)
    
    # Log separato per errori
    error_handler = RotatingFileHandler(
        filename=os.path.join(log_directory, f'{service_name}_error.log'),
        maxBytes=10 * 1024 * 1024,
        backupCount=10
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    error_handler.addFilter(request_context_filter)
    root_logger.addHandler(error_handler)
    
    # Configura log per librerie esterne
    _configure_external_libraries_logging()
    
    # Log di inizializzazione
    logging.info(
        f"Logging configured: level={log_level}, "
        f"environment={environment}, service={service_name}"
    )

def _configure_external_libraries_logging() -> None:
    """
    Configura il livello di logging per librerie esterne.
    
    Riduce il livello di logging per librerie rumorose.
    """
    # Riduci verbosità per alcune librerie
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.pool').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.dialects').setLevel(logging.WARNING)
    
    logging.getLogger('elasticsearch').setLevel(logging.WARNING)
    logging.getLogger('elasticsearch.trace').setLevel(logging.WARNING)
    
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    
    # Security related libraries
    logging.getLogger('passlib').setLevel(logging.WARNING)
    logging.getLogger('jose').setLevel(logging.WARNING)

def set_request_context(request_id=None, user_id=None, ip=None, path=None, method=None, **kwargs):
    """
    Imposta il contesto della richiesta corrente per i log.
    
    Permette di arricchire i log con informazioni sulla richiesta HTTP
    Args:
       request_id (str, optional): ID univoco della richiesta
       user_id (str, optional): ID dell'utente autenticato
       ip (str, optional): Indirizzo IP del client
       path (str, optional): Path della richiesta
       method (str, optional): Metodo HTTP della richiesta
       **kwargs: Altri attributi da aggiungere al contesto
    """
    context = {
        'request_id': request_id or 'no_request_id',
        'user_id': user_id or 'anonymous',
        'ip': ip or '0.0.0.0',
        'path': path or '/',
        'method': method or 'NONE'
    }
    
    # Aggiungi altri attributi
    context.update(kwargs)
    
    # Aggiorna il filtro
    request_context_filter.request_context = context

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Utility per ottenere un logger configurato.
    
    Args:
        name (str, optional): Nome del logger. Se None, usa il logger root.
    
    Returns:
        logging.Logger: Logger configurato
    """
    logger = logging.getLogger(name)
    
    # Assicurati che il logger abbia il nostro filtro di contesto
    for handler in logger.handlers:
        if not any(isinstance(f, type(request_context_filter)) for f in handler.filters):
            handler.addFilter(request_context_filter)
    
    return logger