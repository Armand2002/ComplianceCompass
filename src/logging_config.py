# src/logging_config.py
"""
Configurazione centralizzata del logging per l'applicazione.

Fornisce una configurazione standardizzata per la registrazione 
dei log con formattazione e gestione dei livelli.
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional, Dict, Any

def configure_logging(
    log_level: str = 'INFO', 
    log_dir: Optional[str] = None,
    additional_config: Optional[Dict[str, Any]] = None
) -> None:
    """
    Configura il sistema di logging per l'applicazione.
    
    Args:
        log_level (str, optional): Livello di logging. Defaults a 'INFO'.
        log_dir (str, optional): Directory per i file di log. Se None, usa './logs'.
        additional_config (Dict[str, Any], optional): Configurazioni aggiuntive.
    """
    # Determina la directory dei log
    log_directory = log_dir or os.path.join(os.getcwd(), 'logs')
    
    # Crea la directory dei log se non esiste
    os.makedirs(log_directory, exist_ok=True)
    
    # Configura il logger root
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[]  # Rimuove gli handler predefiniti
    )
    
    # Configurazione logger console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    
    # Configurazione file handler con rotazione
    log_file_path = os.path.join(log_directory, 'compliance_compass.log')
    file_handler = RotatingFileHandler(
        log_file_path, 
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    
    # Logger root
    root_logger = logging.getLogger()
    root_logger.handlers.clear()  # Rimuove eventuali handler esistenti
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Configura log per librerie esterne
    _configure_external_libraries_logging()
    
    # Gestisce configurazioni aggiuntive
    if additional_config:
        _apply_additional_logging_config(additional_config)

def _configure_external_libraries_logging() -> None:
    """
    Configura il livello di logging per librerie esterne.
    
    Riduce il livello di logging per librerie rumorose.
    """
    # Riduci verbosità per alcune librerie
    logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
    logging.getLogger('elasticsearch').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)

def _apply_additional_logging_config(config: Dict[str, Any]) -> None:
    """
    Applica configurazioni di logging aggiuntive.
    
    Args:
        config (Dict[str, Any]): Configurazioni aggiuntive
    """
    # Esempio di configurazione per logger specifici
    if 'loggers' in config:
        for logger_name, logger_config in config['loggers'].items():
            logger = logging.getLogger(logger_name)
            
            # Imposta livello di logging
            if 'level' in logger_config:
                logger.setLevel(getattr(logging, logger_config['level'].upper()))
            
            # Aggiungi handler personalizzati se definiti
            if 'handlers' in logger_config:
                # Implementazione per handler personalizzati
                pass

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Utility per ottenere un logger configurato.
    
    Args:
        name (str, optional): Nome del logger. Se None, usa il logger root.
    
    Returns:
        logging.Logger: Logger configurato
    """
    return logging.getLogger(name)


# Configurazione di default all'importazione
configure_logging()