# src/controllers/faq_controller.py
from typing import List, Dict, Any, Optional
import logging

from src.services.faq_service import FAQService

logger = logging.getLogger(__name__)

class FAQController:
    """
    Controller per la gestione delle FAQ.
    Sostituisce il controller del chatbot.
    """
    
    def __init__(self):
        """Inizializza il controller con il servizio FAQ."""
        self.faq_service = FAQService()
    
    def get_all_faqs(self) -> List[Dict[str, Any]]:
        """
        Ottiene tutte le FAQ.
        
        Returns:
            List[Dict[str, Any]]: Lista di tutte le FAQ
        """
        return self.faq_service.get_all_faqs()
    
    def get_faq_by_id(self, faq_id: int) -> Optional[Dict[str, Any]]:
        """
        Ottiene una FAQ specifica per ID.
        
        Args:
            faq_id (int): ID della FAQ
            
        Returns:
            Optional[Dict[str, Any]]: FAQ trovata o None
        """
        return self.faq_service.get_faq_by_id(faq_id)
    
    def search_faqs(self, query: str) -> Dict[str, Any]:
        """
        Cerca tra le FAQ in base a una query.
        
        Args:
            query (str): Termine di ricerca
            
        Returns:
            Dict[str, Any]: Risultati della ricerca
        """
        results = self.faq_service.search_faqs(query)
        
        return {
            "results": results,
            "total": len(results),
            "query": query
        }
    
    def get_response_for_query(self, query: str) -> Dict[str, Any]:
        """
        Simula una risposta del chatbot cercando nella base FAQ.
        
        Args:
            query (str): Query dell'utente
            
        Returns:
            Dict[str, Any]: Risposta formattata
        """
        if not query:
            return {
                "response": "Come posso aiutarti? Puoi chiedermi informazioni sui Privacy Pattern, GDPR, o come utilizzare la piattaforma.",
                "source": "faq",
                "relevant_faqs": self.faq_service.get_all_faqs()[:3]
            }
        
        matching_faqs = self.faq_service.search_faqs(query)
        
        if matching_faqs:
            best_match = matching_faqs[0]
            return {
                "response": best_match["answer"],
                "source": "faq",
                "faq_id": best_match["id"],
                "question": best_match["question"],
                "relevant_faqs": matching_faqs[1:4] if len(matching_faqs) > 1 else []
            }
        else:
            # Nessuna corrispondenza esatta, restituisci risposta generica
            return {
                "response": "Mi dispiace, non ho una risposta specifica per questa domanda. Prova a riformulare la tua richiesta o consulta le nostre FAQ per argomenti correlati.",
                "source": "fallback",
                "relevant_faqs": self.faq_service.get_all_faqs()[:3]
            }