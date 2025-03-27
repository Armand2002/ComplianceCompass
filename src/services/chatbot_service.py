# src/services/chatbot_service.py
import logging
from typing import Dict, Any, List, Optional
import requests
from sqlalchemy.orm import Session

from src.config import settings
from src.models.privacy_pattern import PrivacyPattern
from src.models.gdpr_model import GDPRArticle

logger = logging.getLogger(__name__)

class ChatbotService:
    """
    Servizio per la gestione del chatbot.
    
    Fornisce funzionalità per rispondere alle domande degli utenti 
    sui Privacy Patterns e normative correlate.
    """
    
    def __init__(self):
        """Inizializza il servizio chatbot."""
        self.api_key = settings.AI_API_KEY
        self.api_endpoint = "https://api.openai.com/v1/chat/completions"
   
    def get_response(self, db: Session, message: str, conversation_history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Ottiene una risposta dal chatbot basata sul messaggio dell'utente.

        Args:
            db (Session): Sessione database
            message (str): Messaggio dell'utente
            conversation_history (List[Dict[str, str]], optional): Storico della conversazione
            
        Returns:
            Dict[str, Any]: Risposta del chatbot con informazioni aggiuntive
        """
        # Inizializza lo storico se non fornito
        if conversation_history is None:
            conversation_history = []
        
        try:
            # Controlla se il messaggio contiene una domanda su un pattern specifico
            pattern_response = self._check_for_pattern_query(db, message)
            if pattern_response:
                return pattern_response
            
            # Controlla se il messaggio contiene una domanda su GDPR
            gdpr_response = self._check_for_gdpr_query(db, message)
            if gdpr_response:
                return gdpr_response
            
            # Altrimenti, utilizza l'API AI per generare una risposta
            if self.api_key:
                return self._get_ai_response(message, conversation_history)
            else:
                # Risposta di fallback se l'API AI non è configurata
                return {
                    "response": "Mi dispiace, non riesco a rispondere a questa domanda al momento. "
                                "Prova a chiedere informazioni su un Privacy Pattern specifico o su un articolo del GDPR.",
                    "source": "fallback"
                }
        except Exception as e:
            logger.error(f"Errore nella generazione della risposta del chatbot: {str(e)}")
            return {
                "response": "Si è verificato un errore durante l'elaborazione della tua richiesta. "
                            "Riprova più tardi o contatta l'assistenza.",
                "source": "error"
            }
    
    def _check_for_pattern_query(self, db: Session, message: str) -> Optional[Dict[str, Any]]:
        """
        Verifica se il messaggio contiene una domanda su un pattern specifico.

        Args:
            db (Session): Sessione database
            message (str): Messaggio dell'utente
            
        Returns:
            Optional[Dict[str, Any]]: Risposta relativa al pattern o None
        """
        # Cerca pattern per titolo
        # Nota: in una implementazione più avanzata, utilizzare NLP per l'intent recognition
        message_lower = message.lower()
        
        # Cerca menzioni di pattern
        patterns = db.query(PrivacyPattern).all()
        for pattern in patterns:
            if pattern.title.lower() in message_lower:
                return {
                    "response": f"**{pattern.title}**\n\n"
                                f"**Descrizione**: {pattern.description}\n\n"
                                f"**Contesto**: {pattern.context}\n\n"
                                f"**Problema**: {pattern.problem}\n\n"
                                f"**Soluzione**: {pattern.solution}\n\n"
                                f"**Strategia**: {pattern.strategy}",
                    "source": "pattern",
                    "pattern_id": pattern.id,
                    "pattern_title": pattern.title
                }
        
        return None
    
    def _check_for_gdpr_query(self, db: Session, message: str) -> Optional[Dict[str, Any]]:
        """
        Verifica se il messaggio contiene una domanda sul GDPR.

        Args:
            db (Session): Sessione database
            message (str): Messaggio dell'utente
            
        Returns:
            Optional[Dict[str, Any]]: Risposta relativa al GDPR o None
        """
        message_lower = message.lower()
        
        # Verifica se la domanda riguarda il GDPR
        if "gdpr" in message_lower or "regolamento" in message_lower:
            # Cerca articoli specifici
            articles = db.query(GDPRArticle).all()
            
            for article in articles:
                article_ref = f"articolo {article.number}"
                if article_ref in message_lower:
                    return {
                        "response": f"**GDPR Articolo {article.number}: {article.title}**\n\n"
                                    f"{article.content}\n\n"
                                    f"**Sintesi**: {article.summary}",
                        "source": "gdpr",
                        "article_id": article.id,
                        "article_number": article.number
                    }
            
            # Se non è stato trovato un articolo specifico, fornisci informazioni generali
            return {
                "response": "Il GDPR (General Data Protection Regulation) è il regolamento europeo sulla protezione dei dati personali.\n\n"
                            "Posso aiutarti a trovare informazioni su articoli specifici o su come applicare il GDPR attraverso i Privacy Patterns. "
                            "Chiedi pure!",
                "source": "gdpr_general"
            }
        
        return None
    
    def _get_ai_response(self, message: str, conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Ottiene una risposta utilizzando l'API AI.

        Args:
            message (str): Messaggio dell'utente
            conversation_history (List[Dict[str, str]]): Storico della conversazione
            
        Returns:
            Dict[str, Any]: Risposta generata dall'AI
        """
        try:
            # Costruisci il contesto per l'API
            system_message = {
                "role": "system",
                "content": "Sei un assistente esperto in Privacy Patterns, GDPR e normative sulla privacy. "
                           "Fornisci risposte accurate e utili sulle normative di privacy, sicurezza informatica "
                           "e implementazione di Privacy Patterns nei sistemi software."
            }
            
            # Costruisci la conversazione
            messages = [system_message]
            
            # Aggiungi storico della conversazione
            for entry in conversation_history:
                messages.append({"role": entry["role"], "content": entry["content"]})
            
            # Aggiungi il messaggio corrente dell'utente
            messages.append({"role": "user", "content": message})
            
            # Richiesta API
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "gpt-3.5-turbo",
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 500
            }
            
            response = requests.post(self.api_endpoint, headers=headers, json=data)
            response.raise_for_status()
            
            response_data = response.json()
            assistant_response = response_data["choices"][0]["message"]["content"]
            
            return {
                "response": assistant_response,
                "source": "ai_api"
            }
        except Exception as e:
            logger.error(f"Errore nella chiamata all'API AI: {str(e)}")
            return {
                "response": "Mi dispiace, al momento non riesco a generare una risposta. "
                            "Prova a formulare la tua domanda in modo diverso o a chiedere "
                            "informazioni specifiche su un Privacy Pattern o sul GDPR.",
                "source": "ai_api_error"
            }
    
    def get_pattern_suggestions(self, db: Session, query: str) -> List[Dict[str, Any]]:
        """
        Ottiene suggerimenti di Privacy Patterns basati sulla query.

        Args:
            db (Session): Sessione database
            query (str): Query dell'utente
            
        Returns:
            List[Dict[str, Any]]: Lista di suggerimenti di pattern
        """
        try:
            # In una implementazione avanzata, utilizzare tecniche di NLP
            # per determinare gli intent e i pattern più rilevanti
            
            # Implementazione semplice basata su keywords
            patterns = db.query(PrivacyPattern).all()
            
            query_lower = query.lower()
            suggestions = []
            
            # Keywords per categorie comuni
            keywords = {
                "anonymity": ["anonimato", "anonimo", "anonymity"],
                "consent": ["consenso", "opt-in", "opt-out"],
                "notification": ["notifica", "avviso", "alert"],
                "access control": ["accesso", "controllo", "autorizzazione"],
                "data minimization": ["minimizzazione", "dati minimi", "minimizzare"],
                "transparency": ["trasparenza", "trasparente", "chiaro"]
            }
            
            # Verifica keywords nella query
            matched_categories = []
            for category, terms in keywords.items():
                if any(term in query_lower for term in terms):
                    matched_categories.append(category)
            
            # Filtra pattern in base alle categorie
            for pattern in patterns:
                # Controlla se il pattern è rilevante per le categorie identificate
                pattern_text = f"{pattern.title} {pattern.description} {pattern.strategy}".lower()
                
                if matched_categories:
                    if any(category.lower() in pattern_text for category in matched_categories):
                        suggestions.append({
                            "id": pattern.id,
                            "title": pattern.title,
                            "description": pattern.description[:100] + "..." if len(pattern.description) > 100 else pattern.description,
                            "strategy": pattern.strategy
                        })
                
                # Aggiungi pattern che corrispondono direttamente alla query
                elif query_lower in pattern_text:
                    suggestions.append({
                        "id": pattern.id,
                        "title": pattern.title,
                        "description": pattern.description[:100] + "..." if len(pattern.description) > 100 else pattern.description,
                        "strategy": pattern.strategy
                    })
            
            # Limita il numero di suggerimenti
            return suggestions[:5]
        except Exception as e:
            logger.error(f"Errore nella generazione dei suggerimenti: {str(e)}")
            return []