"""
Servizi mock per facilitare il testing delle componenti.

Fornisce implementazioni simulate di servizi critici 
per supportare test di unità e integrazione.
"""

from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MockDatabaseSearchService:
    """
    Servizio di ricerca SQL simulato per testing.
    
    Simula le principali operazioni di ricerca database
    senza dipendenze esterne.
    """
    
    def __init__(self):
        """Inizializza il servizio mock."""
        self.documents = {}
        self.is_available = True
    
    def search(
        self, 
        query: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Simula una ricerca nel database.
        
        Args:
            query (Dict[str, Any]): Query di ricerca
        
        Returns:
            Dict[str, Any]: Risultati simulati
        """
        # Simula ricerca base
        matching_docs = [
            doc for doc in self.documents.values()
            if self._match_query(doc, query)
        ]
        
        results = {
            "total": len(matching_docs),
            "results": matching_docs
        }
        return results
    
    def add_document(
        self, 
        document: Dict[str, Any], 
        doc_id: Optional[str] = None
    ) -> str:
        """
        Simula l'aggiunta di un documento.
        
        Args:
            document (Dict[str, Any]): Documento da aggiungere
            doc_id (str, optional): ID documento
        
        Returns:
            str: ID del documento
        """
        # Genera ID se non fornito
        if doc_id is None:
            doc_id = str(len(self.documents) + 1)
        
        self.documents[doc_id] = document
        return doc_id
    
    def remove_document(self, doc_id: str) -> bool:
        """
        Simula la rimozione di un documento.
        
        Args:
            doc_id (str): ID del documento
        
        Returns:
            bool: True se la rimozione è riuscita
        """
        if doc_id in self.documents:
            del self.documents[doc_id]
            return True
        return False
    
    def _match_query(self, document: Dict[str, Any], query: Dict[str, Any]) -> bool:
        """
        Verifica se un documento corrisponde alla query.
        
        Args:
            document (Dict[str, Any]): Documento da verificare
            query (Dict[str, Any]): Query di ricerca
        
        Returns:
            bool: True se il documento corrisponde
        """
        # Implementazione base di matching
        if not query:
            return True
        
        try:
            # Gestione filtri
            filters = query.get("filters", {})
            for field, value in filters.items():
                if field not in document or document[field] != value:
                    return False
            
            # Gestione ricerca testuale
            search_term = query.get("search_term")
            if search_term:
                # Cerca in campi di testo comuni
                text_fields = ["title", "description", "content"]
                found = False
                for field in text_fields:
                    if field in document and search_term.lower() in str(document[field]).lower():
                        found = True
                        break
                
                if not found:
                    return False
            
            return True
        except Exception as e:
            logger.warning(f"Errore durante il matching della query: {e}")
            return False


class MockPatternService:
    """
    Servizio Pattern simulato per testing.
    
    Fornisce un'implementazione mock per test 
    dei servizi di gestione pattern.
    """
    
    def __init__(self):
        """Inizializza il servizio mock."""
        self.patterns = {}
        self._next_id = 1
    
    def get_pattern_by_id(self, pattern_id: int) -> Optional[Dict[str, Any]]:
        """
        Recupera un pattern per ID.
        
        Args:
            pattern_id (int): ID del pattern
        
        Returns:
            Optional[Dict[str, Any]]: Pattern trovato o None
        """
        return self.patterns.get(pattern_id)
    
    def create_pattern(self, pattern_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea un nuovo pattern.
        
        Args:
            pattern_data (Dict[str, Any]): Dati del pattern
        
        Returns:
            Dict[str, Any]: Pattern creato
        """
        # Genera ID
        pattern_id = self._next_id
        self._next_id += 1
        
        # Aggiungi ID e timestamp
        pattern_data['id'] = pattern_id
        pattern_data['created_at'] = datetime.utcnow()
        pattern_data['updated_at'] = datetime.utcnow()
        
        # Implementazione base di validazione
        if 'title' not in pattern_data or not pattern_data['title']:
            raise ValueError("Il campo 'title' è obbligatorio")
        
        if 'description' not in pattern_data or not pattern_data['description']:
            raise ValueError("Il campo 'description' è obbligatorio")
        
        # Salva pattern
        self.patterns[pattern_id] = pattern_data
        return pattern_data
    
    def update_pattern(
        self, 
        pattern_id: int, 
        update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Aggiorna un pattern esistente.
        
        Args:
            pattern_id (int): ID del pattern
            update_data (Dict[str, Any]): Dati da aggiornare
        
        Returns:
            Dict[str, Any]: Pattern aggiornato
        
        Raises:
            ValueError: Se il pattern non esiste
        """
        if pattern_id not in self.patterns:
            raise ValueError(f"Pattern con ID {pattern_id} non trovato")
        
        # Aggiorna dati
        pattern = self.patterns[pattern_id]
        pattern.update(update_data)
        pattern['updated_at'] = datetime.utcnow()
        
        return pattern
    
    def delete_pattern(self, pattern_id: int) -> bool:
        """
        Elimina un pattern.
        
        Args:
            pattern_id (int): ID del pattern
        
        Returns:
            bool: True se l'eliminazione è riuscita
        """
        if pattern_id in self.patterns:
            del self.patterns[pattern_id]
            return True
        return False
    
    def search_patterns(
        self, 
        filters: Optional[Dict[str, Any]] = None,
        search_term: Optional[str] = None,
        page: int = 1,
        per_page: int = 10
    ) -> Dict[str, Any]:
        """
        Ricerca patterns con filtri e paginazione.
        
        Args:
            filters (Dict[str, Any], optional): Filtri di ricerca
            search_term (str, optional): Termine di ricerca testuale
            page (int, optional): Numero di pagina
            per_page (int, optional): Numero di risultati per pagina
        
        Returns:
            Dict[str, Any]: Risultati della ricerca con metadati
        """
        # Filtra i patterns
        filtered_patterns = self._filter_patterns(
            filters, 
            search_term
        )
        
        # Calcola paginazione
        total_count = len(filtered_patterns)
        start_index = (page - 1) * per_page
        end_index = start_index + per_page
        
        # Estrai patterns per la pagina corrente
        paginated_patterns = filtered_patterns[start_index:end_index]
        
        return {
            "patterns": paginated_patterns,
            "total": total_count,
            "page": page,
            "per_page": per_page,
            "total_pages": (total_count + per_page - 1) // per_page
        }
    
    def _filter_patterns(
        self, 
        filters: Optional[Dict[str, Any]] = None,
        search_term: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Filtra i patterns in base a criteri specifici.
        
        Args:
            filters (Dict[str, Any], optional): Filtri specifici
            search_term (str, optional): Termine di ricerca
        
        Returns:
            List[Dict[str, Any]]: Lista dei patterns filtrati
        """
        # Lista di tutti i patterns
        matching_patterns = list(self.patterns.values())
        
        # Applica filtri specifici
        if filters:
            matching_patterns = [
                pattern for pattern in matching_patterns
                if all(
                    pattern.get(key) == value 
                    for key, value in filters.items()
                )
            ]
        
        # Applica ricerca testuale
        if search_term:
            search_term = search_term.lower()
            matching_patterns = [
                pattern for pattern in matching_patterns
                if (
                    search_term in str(pattern.get('title', '')).lower() or
                    search_term in str(pattern.get('description', '')).lower())
            ]
        
        return matching_patterns