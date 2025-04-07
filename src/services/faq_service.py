# src/services/faq_service.py
"""
Servizio FAQ per sostituire il chatbot.
"""
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class FAQService:
    """
    Servizio che fornisce una lista statica di FAQ come alternativa al chatbot.
    """
    
    def __init__(self):
        """Inizializza il servizio FAQ."""
        self.faqs = [
            {
                "id": 1,
                "question": "Cos'è un Privacy Pattern?",
                "answer": "Un Privacy Pattern è una soluzione riutilizzabile per problemi comuni di privacy nella progettazione di sistemi software. I pattern aiutano gli sviluppatori a incorporare best practice di privacy nel loro lavoro."
            },
            {
                "id": 2,
                "question": "Come posso cercare un Privacy Pattern?",
                "answer": "Puoi utilizzare la barra di ricerca nella parte superiore della pagina. Inserisci parole chiave come 'consenso', 'minimizzazione' o 'pseudonimizzazione'. Puoi anche utilizzare i filtri per affinare la tua ricerca."
            },
            {
                "id": 3,
                "question": "Cosa sono i principi Privacy by Design?",
                "answer": "Privacy by Design (PbD) è un approccio che integra la privacy in tutto il ciclo di sviluppo. I suoi sette principi fondamentali includono: Proattività, Privacy come impostazione predefinita, Privacy incorporata nel design, Funzionalità completa, Sicurezza end-to-end, Visibilità/Trasparenza, e Rispetto per la privacy dell'utente."
            },
            {
                "id": 4,
                "question": "Come sono classificati i Privacy Pattern?",
                "answer": "I Privacy Pattern sono classificati per: Strategia (Minimizzazione, Separazione, Astrazione, ecc.), Componente MVC (Model, View, Controller), Fase ISO 9241-210, Articoli GDPR correlati, e Principi Privacy by Design implementati."
            },
            {
                "id": 5,
                "question": "Cos'è il GDPR?",
                "answer": "Il GDPR (General Data Protection Regulation) è un regolamento dell'Unione Europea sulla protezione dei dati e la privacy. Stabilisce regole per la raccolta, l'elaborazione e la conservazione dei dati personali, imponendo obblighi alle organizzazioni e garantendo diritti agli individui."
            },
            {
                "id": 6,
                "question": "Come posso ricevere aggiornamenti sui nuovi Privacy Pattern?",
                "answer": "Puoi iscriverti alla newsletter nella sezione 'Ricevi Notifiche'. Riceverai aggiornamenti su nuovi pattern, miglioramenti e altre novità relative alla piattaforma."
            },
            {
                "id": 7,
                "question": "Cosa indica il componente MVC di un pattern?",
                "answer": "Il componente MVC (Model-View-Controller) indica dove un pattern dovrebbe essere implementato nell'architettura software: Model (dati e logica), View (interfaccia utente), o Controller (gestione delle richieste e coordinamento)."
            },
            {
                "id": 8,
                "question": "Come posso contribuire alla piattaforma?",
                "answer": "Attualmente non è possibile contribuire direttamente, ma puoi fornire feedback tramite la sezione contatti o iscrivendoti alla newsletter per restare aggiornato sulle opportunità future."
            },
            {
                "id": 9,
                "question": "Come faccio a sapere quali pattern soddisfano un articolo specifico del GDPR?",
                "answer": "Puoi utilizzare la ricerca avanzata e selezionare il filtro per articolo GDPR. Ogni pattern mostra anche gli articoli GDPR correlati nella sua pagina di dettaglio."
            },
            {
                "id": 10,
                "question": "Come posso utilizzare gli esempi di implementazione?",
                "answer": "Gli esempi di implementazione forniscono codice e diagrammi come riferimento. Puoi adattarli al tuo contesto specifico, considerandoli come punti di partenza piuttosto che soluzioni complete."
            }
        ]
    
    def get_all_faqs(self) -> List[Dict[str, Any]]:
        """
        Ottiene la lista completa di FAQ.
        
        Returns:
            List[Dict[str, Any]]: Lista di tutte le FAQ
        """
        return self.faqs
    
    def get_faq_by_id(self, faq_id: int) -> Optional[Dict[str, Any]]:
        """
        Ottiene una FAQ specifica per ID.
        
        Args:
            faq_id (int): ID della FAQ da recuperare
            
        Returns:
            Optional[Dict[str, Any]]: FAQ trovata o None
        """
        for faq in self.faqs:
            if faq["id"] == faq_id:
                return faq
        return None
    
    def search_faqs(self, query: str) -> List[Dict[str, Any]]:
        """
        Cerca tra le FAQ in base a una query.
        
        Args:
            query (str): Termine di ricerca
            
        Returns:
            List[Dict[str, Any]]: FAQ corrispondenti alla query
        """
        if not query:
            return self.faqs[:5]  # Restituisci le prime 5 FAQ
        
        query = query.lower()
        results = []
        
        for faq in self.faqs:
            if (query in faq["question"].lower() or 
                query in faq["answer"].lower()):
                results.append(faq)
        
        return results
        
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
                "relevant_faqs": self.get_all_faqs()[:3]
            }
        
        matching_faqs = self.search_faqs(query)
        
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
                "relevant_faqs": self.get_all_faqs()[:3]
            }