# tests/integration/test_pattern_services.py
"""
Test di integrazione per i servizi di gestione dei Privacy Patterns.

Questi test verificano l'interazione tra:
- Pattern Service
- Database
- Gestione delle eccezioni
"""

import pytest
from sqlalchemy.orm import Session
from typing import Dict, Any

from src.services.pattern_service import PatternService
from src.exceptions import (
    DataIntegrityException, 
    ServiceUnavailableException
)
from src.models.privacy_pattern import PrivacyPattern
from src.db.session import SessionLocal
from src.config import settings

@pytest.fixture(scope="module")
def db_session():
    """
    Fixture per ottenere una sessione database per i test di integrazione.
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="module")
def pattern_service(db_session):
    """
    Fixture per il Pattern Service con dipendenze iniettate.
    """
    return PatternService(
        db_session=db_session
    )

class TestPatternServiceIntegration:
    """
    Test di integrazione per il servizio Pattern.
    """
    
    def test_create_pattern_full_flow(self, pattern_service, db_session):
        """
        Test completo del flusso di creazione pattern.
        
        Verifica:
        - Creazione pattern nel database
        - Recupero e validazione
        """
        # Dati di test per un pattern
        pattern_data = {
            "title": "Test Integration Pattern",
            "description": "Un pattern di test per verificare l'integrazione",
            "context": "Scenario di test completo",
            "problem": "Verificare il flusso di creazione",
            "solution": "Implementare test di integrazione robusti",
            "consequences": "Migliorata affidabilità del sistema",
            "strategy": "Integrate",
            "mvc_component": "Controller"
        }
        
        # Crea il pattern
        created_pattern = pattern_service.create_pattern(pattern_data)
        
        # Verifica creazione nel database
        assert created_pattern is not None
        assert created_pattern.id is not None
        assert created_pattern.title == pattern_data["title"]
        
        # Recupera il pattern dal database per conferma
        retrieved_pattern = pattern_service.get_pattern_by_id(created_pattern.id)
        assert retrieved_pattern is not None
        assert retrieved_pattern.title == pattern_data["title"]
    
    def test_update_pattern(
        self, 
        pattern_service, 
        db_session
    ):
        """
        Test di aggiornamento pattern.
        
        Verifica:
        - Aggiornamento pattern nel database
        """
        # Crea un pattern di test
        initial_data = {
            "title": "Pattern da Aggiornare",
            "description": "Pattern iniziale per test di aggiornamento",
            "strategy": "Initial",
            "mvc_component": "Model"
        }
        initial_pattern = pattern_service.create_pattern(initial_data)
        
        # Dati di aggiornamento
        update_data = {
            "title": "Pattern Aggiornato",
            "strategy": "Updated"
        }
        
        # Aggiorna il pattern
        updated_pattern = pattern_service.update_pattern(
            initial_pattern.id, 
            update_data
        )
        
        # Verifica aggiornamenti
        assert updated_pattern.title == "Pattern Aggiornato"
        assert updated_pattern.strategy == "Updated"
        
        # Verifica che l'ID rimanga invariato
        assert updated_pattern.id == initial_pattern.id
    
    def test_search_patterns(
        self, 
        pattern_service, 
        db_session
    ):
        """
        Test di ricerca pattern.
        
        Verifica:
        - Ricerca con filtri multipli
        """
        # Crea alcuni pattern di test
        test_patterns = [
            {
                "title": "Pattern Ricerca 1",
                "description": "Pattern per test di ricerca",
                "strategy": "Search",
                "mvc_component": "Controller"
            },
            {
                "title": "Pattern Ricerca 2",
                "description": "Altro pattern per test di ricerca",
                "strategy": "Search",
                "mvc_component": "Model"
            }
        ]
        
        # Crea pattern
        for pattern_data in test_patterns:
            pattern_service.create_pattern(pattern_data)
        
        # Esegui ricerca
        search_results = pattern_service.search_patterns(
            filters={"strategy": "Search"},
            page=1,
            per_page=10
        )
        
        # Verifica risultati
        assert search_results['total'] >= 2
        assert len(search_results['patterns']) > 0
        assert all(
            pattern.strategy == "Search" 
            for pattern in search_results['patterns']
        )
    
    def test_delete_pattern(
        self, 
        pattern_service, 
        db_session
    ):
        """
        Test di eliminazione pattern.
        
        Verifica:
        - Eliminazione dal database
        """
        # Crea un pattern di test
        pattern_data = {
            "title": "Pattern da Eliminare",
            "description": "Pattern per test di eliminazione",
            "strategy": "Delete",
            "mvc_component": "View"
        }
        pattern = pattern_service.create_pattern(pattern_data)
        
        # Elimina il pattern
        deletion_result = pattern_service.delete_pattern(pattern.id)
        
        # Verifica eliminazione
        assert deletion_result is True
        
        # Verifica che il pattern non sia più recuperabile
        retrieved_pattern = pattern_service.get_pattern_by_id(pattern.id)
        assert retrieved_pattern is None
    
    def test_error_handling(self, pattern_service):
        """
        Test gestione degli errori.
        
        Verifica:
        - Gestione eccezioni di integrità
        - Gestione pattern non validi
        """
        # Test creazione con dati non validi
        with pytest.raises(DataIntegrityException):
            pattern_service.create_pattern({
                # Dati mancanti o non validi
                "title": "",  # Titolo vuoto
                "description": "Descrizione parziale"
            })
        
        # Test recupero pattern inesistente
        non_existent_pattern = pattern_service.get_pattern_by_id(99999)
        assert non_existent_pattern is None

def test_db_search(
    pattern_service, 
    db_session
):
    """
    Test del meccanismo di ricerca database.
    
    Verifica il comportamento della ricerca basata su SQL.
    """
    # Crea un pattern
    pattern_data = {
        "title": "SQL Search Pattern",
        "description": "Test del meccanismo di ricerca SQL",
        "strategy": "Search",
        "mvc_component": "Controller"
    }
    
    # Crea il pattern
    created_pattern = pattern_service.create_pattern(pattern_data)
    
    # Verifica creazione nel database
    assert created_pattern is not None
    assert created_pattern.title == "SQL Search Pattern"
    
    # Esegui una ricerca
    results = pattern_service.search_service.search_patterns(
        db=db_session,
        query="SQL Search",
        strategy="Search"
    )
    
    # Verifica risultati
    assert results["total"] >= 1
    assert any(p["id"] == created_pattern.id for p in results["results"])