# tests/integration/test_pattern_routes.py
"""
Test di integrazione per le rotte API relative ai Privacy Patterns.

Verifica il funzionamento corretto degli endpoint REST.
"""
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
            "description": "Too short"        }
        
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
        nonexistent_id = 99999
        
        # Act
        response = client.delete(f"/api/patterns/{nonexistent_id}", headers=headers)
        
        # Assert
        assert response.status_code == 404
    
    def test_get_patterns_with_filters(self, client, user_token, db):
        """Verifica il filtraggio dei pattern."""
        # Arrange
        headers = {"Authorization": f"Bearer {user_token}"}
        
        # Act
        response = client.get(
            "/api/patterns/?strategy=Test&mvc_component=Model", 
            headers=headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "patterns" in data
        assert all(p["strategy"] == "Test" for p in data["patterns"])
        assert all(p["mvc_component"] == "Model" for p in data["patterns"])
    
    def test_get_pattern_stats(self, client, user_token, db):
        """Verifica le statistiche dei pattern."""
        # Arrange
        headers = {"Authorization": f"Bearer {user_token}"}
        
        # Act
        response = client.get("/api/patterns/stats", headers=headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "total_patterns" in data
        assert "patterns_by_strategy" in data
        assert "patterns_by_mvc" in data
    
    def test_get_patterns_by_strategy(self, client, user_token, db):
        """Verifica il raggruppamento dei pattern per strategia."""
        # Arrange
        headers = {"Authorization": f"Bearer {user_token}"}
        
        # Act
        response = client.get("/api/patterns/by-strategy", headers=headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        for strategy_group in data:
            assert "strategy" in strategy_group
            assert "patterns" in strategy_group
    
    def test_get_patterns_by_mvc(self, client, user_token, db):
        """Verifica il raggruppamento dei pattern per componente MVC."""
        # Arrange
        headers = {"Authorization": f"Bearer {user_token}"}
        
        # Act
        response = client.get("/api/patterns/by-mvc", headers=headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        for mvc_group in data:
            assert "mvc_component" in mvc_group
            assert "patterns" in mvc_group
    
    def test_get_related_patterns(self, client, user_token, db):
        """Verifica il recupero dei pattern correlati."""
        # Arrange
        headers = {"Authorization": f"Bearer {user_token}"}
        # Prima creiamo un pattern
        pattern_data = {
            "title": "Pattern for Related",
            "description": "Test pattern for related patterns",
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
        response = client.get(f"/api/patterns/{pattern_id}/related", headers=headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        for pattern in data:
            assert "id" in pattern
            assert "title" in pattern
            assert "similarity_score" in pattern
    
    def test_get_patterns_pagination(self, client, user_token, db):
        """Verifica la paginazione dei pattern."""
        # Arrange
        headers = {"Authorization": f"Bearer {user_token}"}
        
        # Act
        response = client.get("/api/patterns/?page=1&per_page=5", headers=headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "patterns" in data
        assert "total" in data
        assert "page" in data
        assert "pages" in data
        assert len(data["patterns"]) <= 5
    
    def test_get_patterns_with_combined_filters(self, client, user_token, db):
        """Verifica il filtraggio combinato dei pattern."""
        # Arrange
        headers = {"Authorization": f"Bearer {user_token}"}
        
        # Act
        response = client.get(
            "/api/patterns/?strategy=Test&mvc_component=Model&search=test",
            headers=headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        for pattern in data["patterns"]:
            assert pattern["strategy"] == "Test"
            assert pattern["mvc_component"] == "Model"
    
    def test_error_handling_invalid_parameters(self, client, user_token):
        """Verifica la gestione degli errori per parametri non validi."""
        # Arrange
        headers = {"Authorization": f"Bearer {user_token}"}
        
        # Test con page invalida
        response1 = client.get("/api/patterns/?page=0", headers=headers)
        assert response1.status_code == 422
        
        # Test con per_page invalido
        response2 = client.get("/api/patterns/?per_page=0", headers=headers)
        assert response2.status_code == 422
        
        # Test con strategia non valida
        response3 = client.get("/api/patterns/?strategy=InvalidStrategy", headers=headers)
        assert response3.status_code == 422