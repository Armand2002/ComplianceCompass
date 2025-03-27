# tests/integration/test_pattern_routes.py
"""
Test di integrazione per le rotte API relative ai Privacy Patterns.

Verifica il funzionamento corretto degli endpoint REST.
"""
import pytest
from fastapi.testclient import TestClient


class TestPatternRoutes:
    """Test per le rotte dei Privacy Pattern."""
    
    def test_get_patterns_no_auth(self, client):
        """Verifica che l'elenco dei pattern richieda autenticazione."""
        # Act
        response = client.get("/api/patterns/")
        
        # Assert
        assert response.status_code == 401
    
    def test_get_patterns_with_auth(self, client, user_token, db):
        """Verifica che un utente autenticato possa ottenere l'elenco dei pattern."""
        # Arrange
        headers = {"Authorization": f"Bearer {user_token}"}
        
        # Act
        response = client.get("/api/patterns/", headers=headers)
        
        # Assert
        assert response.status_code == 200
        assert "patterns" in response.json()
        assert "total" in response.json()
        assert "page" in response.json()
    
    def test_create_pattern_no_auth(self, client):
        """Verifica che la creazione di un pattern richieda autenticazione."""
        # Arrange
        pattern_data = {
            "title": "Test Pattern",
            "description": "This is a test pattern",
            "context": "Test context for the pattern",
            "problem": "Test problem that the pattern solves",
            "solution": "Test solution provided by the pattern",
            "consequences": "Test consequences of applying the pattern",
            "strategy": "Test",
            "mvc_component": "Model"
        }
        
        # Act
        response = client.post("/api/patterns/", json=pattern_data)
        
        # Assert
        assert response.status_code == 401
    
    def test_create_pattern_with_auth(self, client, user_token, db):
        """Verifica che un utente autenticato possa creare un pattern."""
        # Arrange
        headers = {"Authorization": f"Bearer {user_token}"}
        pattern_data = {
            "title": "Test Pattern",
            "description": "This is a test pattern",
            "context": "Test context for the pattern",
            "problem": "Test problem that the pattern solves",
            "solution": "Test solution provided by the pattern",
            "consequences": "Test consequences of applying the pattern",
            "strategy": "Test",
            "mvc_component": "Model"
        }
        
        # Act
        response = client.post("/api/patterns/", json=pattern_data, headers=headers)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Pattern"
        assert data["strategy"] == "Test"
        assert data["mvc_component"] == "Model"
        assert "id" in data
    
    def test_get_pattern_by_id(self, client, user_token, db):
        """Verifica che un utente possa recuperare un pattern specifico per ID."""
        # Arrange
        headers = {"Authorization": f"Bearer {user_token}"}
        # Prima creiamo un pattern
        pattern_data = {
            "title": "Get By ID Pattern",
            "description": "This is a test pattern for getting by ID",
            "context": "Test context for the pattern",
            "problem": "Test problem that the pattern solves",
            "solution": "Test solution provided by the pattern",
            "consequences": "Test consequences of applying the pattern",
            "strategy": "Test",
            "mvc_component": "Model"
        }
        create_response = client.post("/api/patterns/", json=pattern_data, headers=headers)
        pattern_id = create_response.json()["id"]
        
        # Act
        response = client.get(f"/api/patterns/{pattern_id}", headers=headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == pattern_id
        assert data["title"] == "Get By ID Pattern"
    
    def test_get_nonexistent_pattern(self, client, user_token):
        """Verifica che la richiesta di un pattern inesistente restituisca 404."""
        # Arrange
        headers = {"Authorization": f"Bearer {user_token}"}
        nonexistent_id = 99999  # ID molto alto che probabilmente non esiste
        
        # Act
        response = client.get(f"/api/patterns/{nonexistent_id}", headers=headers)
        
        # Assert
        assert response.status_code == 404
    
    def test_update_pattern(self, client, user_token, db):
        """Verifica che un utente possa aggiornare un pattern esistente."""
        # Arrange
        headers = {"Authorization": f"Bearer {user_token}"}
        # Prima creiamo un pattern
        pattern_data = {
            "title": "Pattern To Update",
            "description": "This is a test pattern for updating",
            "context": "Original context",
            "problem": "Original problem",
            "solution": "Original solution",
            "consequences": "Original consequences",
            "strategy": "Original",
            "mvc_component": "Model"
        }
        create_response = client.post("/api/patterns/", json=pattern_data, headers=headers)
        pattern_id = create_response.json()["id"]
        
        # Dati per l'aggiornamento
        update_data = {
            "title": "Updated Pattern",
            "description": "This pattern has been updated",
            "strategy": "Updated"
        }
        
        # Act
        response = client.put(f"/api/patterns/{pattern_id}", json=update_data, headers=headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == pattern_id
        assert data["title"] == "Updated Pattern"
        assert data["description"] == "This pattern has been updated"
        assert data["strategy"] == "Updated"
        # Verifica che i campi non aggiornati rimangano invariati
        assert data["context"] == "Original context"
        assert data["problem"] == "Original problem"
    
    def test_update_nonexistent_pattern(self, client, user_token):
        """Verifica che l'aggiornamento di un pattern inesistente restituisca 404."""
        # Arrange
        headers = {"Authorization": f"Bearer {user_token}"}
        nonexistent_id = 99999  # ID molto alto che probabilmente non esiste
        update_data = {
            "title": "Updated Nonexistent Pattern",
            "description": "This pattern does not exist"
        }
        
        # Act
        response = client.put(f"/api/patterns/{nonexistent_id}", json=update_data, headers=headers)
        
        # Assert
        assert response.status_code == 404
    
    def test_update_pattern_invalid_data(self, client, user_token, db):
        """Verifica che l'aggiornamento con dati non validi restituisca un errore."""
        # Arrange
        headers = {"Authorization": f"Bearer {user_token}"}
        # Prima creiamo un pattern
        pattern_data = {
            "title": "Pattern For Invalid Update",
            "description": "This is a test pattern for invalid update",
            "context": "Test context",
            "problem": "Test problem",
            "solution": "Test solution",
            "consequences": "Test consequences",
            "strategy": "Test",
            "mvc_component": "Model"
        }
        create_response = client.post("/api/patterns/", json=pattern_data, headers=headers)
        pattern_id = create_response.json()["id"]
        
        # Dati non validi (description troppo corta)
        invalid_data = {
            "description": "Too short"  # Dovrebbe avere min_length=10
        }
        
        # Act
        response = client.put(f"/api/patterns/{pattern_id}", json=invalid_data, headers=headers)
        
        # Assert
        assert response.status_code == 422  # Unprocessable Entity
    
    def test_delete_pattern(self, client, user_token, db):
        """Verifica che un utente possa eliminare un pattern esistente."""
        # Arrange
        headers = {"Authorization": f"Bearer {user_token}"}
        # Prima creiamo un pattern
        pattern_data = {
            "title": "Pattern To Delete",
            "description": "This is a test pattern for deletion",
            "context": "Test context for the pattern",
            "problem": "Test problem that the pattern solves",
            "solution": "Test solution provided by the pattern",
            "consequences": "Test consequences of applying the pattern",
            "strategy": "Test",
            "mvc_component": "Model"
        }
        create_response = client.post("/api/patterns/", json=pattern_data, headers=headers)
        pattern_id = create_response.json()["id"]
        
        # Act
        response = client.delete(f"/api/patterns/{pattern_id}", headers=headers)
        
        # Assert
        assert response.status_code == 204
        
        # Verifica che il pattern non esista più
        get_response = client.get(f"/api/patterns/{pattern_id}", headers=headers)
        assert get_response.status_code == 404
    
    def test_delete_nonexistent_pattern(self, client, user_token):
        """Verifica che l'eliminazione di un pattern inesistente restituisca 404."""
        # Arrange
        headers = {"Authorization": f"Bearer {user_token}"}
        nonexistent_id = 99999  # ID molto alto che probabilmente non esiste
        
        # Act
        response = client.delete(f"/api/patterns/{nonexistent_id}", headers=headers)
        
        # Assert
        assert response.status_code == 404
    
    def test_get_patterns_with_filters(self, client, user_token, db):
        """Verifica che si possano filtrare i pattern per vari criteri."""
        # Arrange
        headers = {"Authorization": f"Bearer {user_token}"}
        # Crea alcuni pattern con diverse caratteristiche
        pattern1 = {
            "title": "Pattern Strategy A",
            "description": "This is a test pattern with strategy A",
            "context": "Test context",
            "problem": "Test problem",
            "solution": "Test solution",
            "consequences": "Test consequences",
            "strategy": "StrategyA",
            "mvc_component": "Model"
        }
        pattern2 = {
            "title": "Pattern Strategy B",
            "description": "This is a test pattern with strategy B",
            "context": "Test context",
            "problem": "Test problem",
            "solution": "Test solution",
            "consequences": "Test consequences",
            "strategy": "StrategyB",
            "mvc_component": "View"
        }
        client.post("/api/patterns/", json=pattern1, headers=headers)
        client.post("/api/patterns/", json=pattern2, headers=headers)
        
        # Act - Filtra per strategia
        response_strategy = client.get("/api/patterns/?strategy=StrategyA", headers=headers)
        # Act - Filtra per componente MVC
        response_mvc = client.get("/api/patterns/?mvc_component=View", headers=headers)
        # Act - Filtra per termine di ricerca
        response_search = client.get("/api/patterns/?search=Strategy+A", headers=headers)
        
        # Assert
        assert response_strategy.status_code == 200
        strategy_data = response_strategy.json()
        assert len(strategy_data["patterns"]) > 0
        assert all(p["strategy"] == "StrategyA" for p in strategy_data["patterns"])
        
        assert response_mvc.status_code == 200
        mvc_data = response_mvc.json()
        assert len(mvc_data["patterns"]) > 0
        assert all(p["mvc_component"] == "View" for p in mvc_data["patterns"])
        
        assert response_search.status_code == 200
        search_data = response_search.json()
        assert len(search_data["patterns"]) > 0
    
    def test_get_pattern_stats(self, client, user_token, db):
        """Verifica che si possano ottenere statistiche sui pattern."""
        # Arrange
        headers = {"Authorization": f"Bearer {user_token}"}
        # Crea alcuni pattern con diverse caratteristiche
        pattern1 = {
            "title": "Stats Pattern A",
            "description": "Pattern for stats test",
            "context": "Test context",
            "problem": "Test problem",
            "solution": "Test solution",
            "consequences": "Test consequences",
            "strategy": "StatA",
            "mvc_component": "Model"
        }
        pattern2 = {
            "title": "Stats Pattern B",
            "description": "Pattern for stats test",
            "context": "Test context",
            "problem": "Test problem",
            "solution": "Test solution",
            "consequences": "Test consequences",
            "strategy": "StatB",
            "mvc_component": "View"
        }
        client.post("/api/patterns/", json=pattern1, headers=headers)
        client.post("/api/patterns/", json=pattern2, headers=headers)
        
        # Act
        response = client.get("/api/patterns/stats", headers=headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "strategies" in data
        assert "mvc_components" in data
        assert data["total"] > 0
        assert len(data["strategies"]) > 0
        assert len(data["mvc_components"]) > 0
    
    def test_get_patterns_by_strategy(self, client, user_token, db):
        """Verifica l'endpoint di ricerca pattern per strategia."""
        # Arrange
        headers = {"Authorization": f"Bearer {user_token}"}
        # Crea pattern con specifica strategia
        pattern_data = {
            "title": "Pattern By Strategy",
            "description": "This is a test pattern for strategy endpoint",
            "context": "Test context",
            "problem": "Test problem",
            "solution": "Test solution",
            "consequences": "Test consequences",
            "strategy": "UniqueStrategy",
            "mvc_component": "Model"
        }
        client.post("/api/patterns/", json=pattern_data, headers=headers)
        
        # Act
        response = client.get("/api/patterns/by-strategy/UniqueStrategy", headers=headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert all(p["strategy"] == "UniqueStrategy" for p in data)
    
    def test_get_patterns_by_mvc(self, client, user_token, db):
        """Verifica l'endpoint di ricerca pattern per componente MVC."""
        # Arrange
        headers = {"Authorization": f"Bearer {user_token}"}
        # Crea pattern con specifico componente MVC
        pattern_data = {
            "title": "Pattern By MVC",
            "description": "This is a test pattern for MVC endpoint",
            "context": "Test context",
            "problem": "Test problem",
            "solution": "Test solution",
            "consequences": "Test consequences",
            "strategy": "Test",
            "mvc_component": "Controller"
        }
        client.post("/api/patterns/", json=pattern_data, headers=headers)
        
        # Act
        response = client.get("/api/patterns/by-mvc/Controller", headers=headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert all(p["mvc_component"] == "Controller" for p in data)
    
    def test_get_related_patterns(self, client, user_token, db):
        """Verifica l'endpoint per ottenere pattern correlati."""
        # Arrange
        headers = {"Authorization": f"Bearer {user_token}"}
        # Crea alcuni pattern con caratteristiche simili
        pattern1 = {
            "title": "Related Pattern 1",
            "description": "This is a test pattern for related patterns",
            "context": "Test context",
            "problem": "Test problem",
            "solution": "Test solution",
            "consequences": "Test consequences",
            "strategy": "RelatedStrategy",
            "mvc_component": "Model"
        }
        pattern2 = {
            "title": "Related Pattern 2",
            "description": "This is another test pattern that is related",
            "context": "Test context",
            "problem": "Test problem",
            "solution": "Test solution",
            "consequences": "Test consequences",
            "strategy": "RelatedStrategy",
            "mvc_component": "Model"
        }
        
        response1 = client.post("/api/patterns/", json=pattern1, headers=headers)
        client.post("/api/patterns/", json=pattern2, headers=headers)
        pattern_id = response1.json()["id"]
        
        # Act
        response = client.get(f"/api/patterns/related/{pattern_id}", headers=headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        # Dovrebbe avere almeno un pattern correlato (pattern2)
        assert len(data) > 0