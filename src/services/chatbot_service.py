# src/services/chatbot_service.py
import logging
import os
from typing import Dict, Any, List, Optional
import requests
from sqlalchemy.orm import Session

from src.config import settings
from src.models.privacy_pattern import PrivacyPattern
from src.models.gdpr_model import GDPRArticle

logger = logging.getLogger(__name__)

class ChatbotService:
    """Servizio per il chatbot intelligente"""
    
    def __init__(self):
        # Controllo se usare la versione semplificata per demo/esame
        if getattr(settings, 'USE_SIMPLE_CHATBOT', False):
            try:
                from src.services.mock.chatbot_service import SimpleChatbotService
                self.service = SimpleChatbotService()
                logger.info("Utilizzando versione semplificata del chatbot per modalità demo")
                return
            except ImportError:
                logger.warning("Versione semplificata del chatbot non disponibile, tentativo di inizializzare completo")
        
        # Inizializzazione completa con NLP
        try:
            # Importo qui per evitare dipendenze non necessarie in modalità demo
            import torch
            from transformers import AutoTokenizer, AutoModel
            
            # Resto dell'inizializzazione del modello NLP
            # ...
            
        except Exception as e:
            logger.error(f"Errore durante l'inizializzazione del chatbot: {e}")
            # Fallback alla versione semplice
            from src.services.mock.chatbot_service import SimpleChatbotService
            self.service = SimpleChatbotService()
    
    def generate_response(self, query: str) -> str:
        """Genera una risposta basata sulla query dell'utente"""
        return self.service.generate_response(query)