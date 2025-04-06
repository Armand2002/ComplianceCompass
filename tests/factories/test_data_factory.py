# tests/factories/test_data_factory.py
"""
Factory per generare dati di test consistenti e riutilizzabili.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import random
import string

class TestDataFactory:
    """Factory per generare dati di test consistenti e parametrizzabili."""
    
    @staticmethod
    def create_pattern_data(
        strategy: str = "Minimize",
        mvc_component: str = "Model",
        complexity: str = "medium",
        custom_title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Crea dati per un pattern di test con complessità variabile.
        
        Args:
            strategy: Strategia del pattern
            mvc_component: Componente MVC
            complexity: Complessità del pattern ('low', 'medium', 'high')
            custom_title: Titolo personalizzato o None per titolo generato
            
        Returns:
            Dict con dati del pattern
        """
        # Genera un titolo casuale se non specificato
        if custom_title is None:
            random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            custom_title = f"Test Pattern {strategy}-{random_suffix}"
            
        base_data = {
            "title": custom_title,
            "description": f"Description for test pattern using {strategy} strategy",
            "context": f"Context for {strategy} pattern in {mvc_component}",
            "problem": "Generic privacy problem that needs to be solved",
            "solution": f"Implementation of {strategy} strategy in {mvc_component} component",
            "consequences": "Improved privacy and compliance with regulations",
            "strategy": strategy,
            "mvc_component": mvc_component
        }
        
        # Aggiunge dati in base alla complessità
        if complexity == "low":
            # Dati minimi
            pass
            
        elif complexity == "medium":
            # Dati standard
            base_data.update({
                "gdpr_ids": [5, 25],
                "pbd_ids": [1],
                "iso_ids": [3],
                "vulnerability_ids": [1]
            })
            
        elif complexity == "high":
            # Dati completi
            base_data.update({
                "gdpr_ids": [5, 6, 25, 32],
                "pbd_ids": [1, 2, 3],
                "iso_ids": [2, 3, 4],
                "vulnerability_ids": [1, 3, 6]
            })
            
        return base_data
    
    @staticmethod
    def create_user_data(
        role: str = "VIEWER",
        is_active: bool = True,
        custom_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Crea dati per un utente di test.
        
        Args:
            role: Ruolo dell'utente ('ADMIN', 'EDITOR', 'VIEWER')
            is_active: Se l'utente è attivo
            custom_email: Email personalizzata o None per email generata
            
        Returns:
            Dict con dati dell'utente
        """
        # Genera email casuale se non specificata
        if custom_email is None:
            random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
            custom_email = f"test.{random_suffix}@example.com"
            
        return {
            "email": custom_email,
            "username": custom_email.split('@')[0],
            "password": "password123",
            "full_name": f"Test User ({role})",
            "role": role,
            "is_active": is_active,
            "bio": f"This is a test user with {role} role",
            "avatar_url": None
        }
    
    @staticmethod
    def create_query_params(
        search_term: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """
        Crea parametri di query per test di ricerca.
        
        Args:
            search_term: Termine di ricerca
            filters: Filtri aggiuntivi
            page: Numero di pagina
            page_size: Dimensione della pagina
            
        Returns:
            Dict con parametri di query
        """
        params = {
            "skip": (page - 1) * page_size,
            "limit": page_size
        }
        
        if search_term:
            params["search"] = search_term
            
        if filters:
            params.update(filters)
            
        return params