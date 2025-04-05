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
        test_strategy = "UniqueStrategyTest"
        pattern_data = {
            "title": "Strategy Specific Pattern",
            "description": "Pattern for strategy test",
            "context": "Test context",
            "problem": "Test problem",
            "solution": "Test solution",
            "consequences": "Test consequences",
            "strategy": test_strategy,
            "mvc_component": "Model"
        }
        client.post("/api/patterns/", json=pattern_data, headers=headers)
        
        # Act
        response = client.get(f"/api/patterns/by-strategy/{test_strategy}", headers=headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert all(p["strategy"] == test_strategy for p in data)
    
    def test_get_patterns_by_mvc(self, client, user_token, db):
        """Verifica l'endpoint di ricerca pattern per componente MVC."""
        # Arrange
        headers = {"Authorization": f"Bearer {user_token}"}
        # Crea pattern con specifico componente MVC
        test_component = "Controller"
        pattern_data = {
            "title": "MVC Specific Pattern",
            "description": "Pattern for MVC component test",
            "context": "Test context",
            "problem": "Test problem",
            "solution": "Test solution",
            "consequences": "Test consequences",
            "strategy": "TestStrategy",
            "mvc_component": test_component
        }
        client.post("/api/patterns/", json=pattern_data, headers=headers)
        
        # Act
        response = client.get(f"/api/patterns/by-mvc/{test_component}", headers=headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert all(p["mvc_component"] == test_component for p in data)
    
    def test_get_related_patterns(self, client, user_token, db):
        """Verifica l'endpoint di recupero pattern correlati."""
        # Arrange
        headers = {"Authorization": f"Bearer {user_token}"}
        
        # Crea un pattern principale e alcuni pattern correlati
        main_pattern = {
            "title": "Main Related Pattern",
            "description": "This is the main pattern for testing related patterns",
            "context": "Test context for related patterns",
            "problem": "Test problem for related patterns",
            "solution": "Test solution for related patterns",
            "consequences": "Test consequences for related patterns",
            "strategy": "RelatedTest",
            "mvc_component": "Model"
        }
        
        main_response = client.post("/api/patterns/", json=main_pattern, headers=headers)
        main_pattern_id = main_response.json()["id"]
        
        # Crea altri pattern che dovrebbero essere correlati
        for i in range(5):
            related_pattern = {
                "title": f"Related Pattern {i}",
                "description": "This is a pattern related to the main pattern",
                "context": "Similar context to main pattern",
                "problem": "Similar problem to main pattern",
                "solution": "Similar solution to main pattern",
                "consequences": "Similar consequences to main pattern",
                "strategy": "RelatedTest",  # Stessa strategia per garantire correlazione
                "mvc_component": "Model"
            }
            client.post("/api/patterns/", json=related_pattern, headers=headers)
        
        # Act
        response = client.get(f"/api/patterns/related/{main_pattern_id}", headers=headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        for pattern in data:
            assert pattern["id"] != main_pattern_id  # Non dovrebbe includere il pattern principale
        
        # Verifica il caso di pattern inesistente
        nonexistent_id = 99999
        error_response = client.get(f"/api/patterns/related/{nonexistent_id}", headers=headers)
        assert error_response.status_code == 404
    
    def test_get_patterns_pagination(self, client, user_token, db):
        """Verifica che la paginazione funzioni correttamente."""
        # Arrange
        headers = {"Authorization": f"Bearer {user_token}"}
        
        # Crea 25 pattern di test
        for i in range(25):
            pattern_data = {
                "title": f"Test Pattern {i}",
                "description": f"Test description {i}",
                "context": "Test context",
                "problem": "Test problem",
                "solution": "Test solution",
                "consequences": "Test consequences",
                "strategy": "Test",
                "mvc_component": "Model"
            }
            client.post("/api/patterns/", json=pattern_data, headers=headers)
        
        # Act - Richiedi prima pagina (10 risultati)
        response1 = client.get("/api/patterns/?limit=10&skip=0", headers=headers)
        
        # Act - Richiedi seconda pagina (10 risultati)
        response2 = client.get("/api/patterns/?limit=10&skip=10", headers=headers)
        
        # Act - Richiedi terza pagina (5 risultati)
        response3 = client.get("/api/patterns/?limit=10&skip=20", headers=headers)
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response3.status_code == 200
        
        data1 = response1.json()
        data2 = response2.json()
        data3 = response3.json()
        
        assert len(data1["patterns"]) == 10
        assert len(data2["patterns"]) == 10
        assert len(data3["patterns"]) >= 5  # Almeno 5 risultati
        
        # Verifica che i pattern siano diversi tra le pagine
        page1_ids = {p["id"] for p in data1["patterns"]}
        page2_ids = {p["id"] for p in data2["patterns"]}
        page3_ids = {p["id"] for p in data3["patterns"]}
        
        assert not page1_ids.intersection(page2_ids)
        assert not page1_ids.intersection(page3_ids)
        assert not page2_ids.intersection(page3_ids)
        
        # Verifica che i metadati di paginazione siano corretti
        assert data1["total"] >= 25
        assert data1["page"] == 1
        assert data1["size"] == 10
        assert data1["pages"] >= 3
        
        assert data2["page"] == 2
        assert data3["page"] == 3
    
    def test_get_patterns_with_combined_filters(self, client, user_token, db):
        """Verifica che i filtri combinati funzionino correttamente."""
        # Arrange
        headers = {"Authorization": f"Bearer {user_token}"}
        
        # Crea pattern con strategie e componenti MVC diversi
        strategies = ["Minimize", "Hide", "Separate", "Aggregate", "Inform"]
        mvc_components = ["Model", "View", "Controller"]
        
        for i, strategy in enumerate(strategies):
            for j, component in enumerate(mvc_components):
                pattern_data = {
                    "title": f"Test Pattern {strategy} {component}",
                    "description": f"Pattern using {strategy} strategy in {component}",
                    "context": "Test context",
                    "problem": "Test problem",
                    "solution": "Test solution",
                    "consequences": "Test consequences",
                    "strategy": strategy,
                    "mvc_component": component
                }
                client.post("/api/patterns/", json=pattern_data, headers=headers)
        
        # Act - Filtra per strategia
        response1 = client.get("/api/patterns/?strategy=Minimize", headers=headers)
        
        # Act - Filtra per componente MVC
        response2 = client.get("/api/patterns/?mvc_component=Model", headers=headers)
        
        # Act - Filtra per strategia E componente MVC
        response3 = client.get("/api/patterns/?strategy=Minimize&mvc_component=Model", headers=headers)
        
        # Act - Filtra con ricerca testuale
        response4 = client.get("/api/patterns/?search=Hide", headers=headers)
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response3.status_code == 200
        assert response4.status_code == 200
        
        data1 = response1.json()
        data2 = response2.json()
        data3 = response3.json()
        data4 = response4.json()
        
        # Verifica filtro per strategia
        assert all(p["strategy"] == "Minimize" for p in data1["patterns"])
        assert len(data1["patterns"]) == 3  # Uno per ogni componente MVC
        
        # Verifica filtro per componente MVC
        assert all(p["mvc_component"] == "Model" for p in data2["patterns"])
        assert len(data2["patterns"]) == 5  # Uno per ogni strategia
        
        # Verifica filtro combinato
        assert all(p["strategy"] == "Minimize" and p["mvc_component"] == "Model" for p in data3["patterns"])
        assert len(data3["patterns"]) == 1
        
        # Verifica ricerca testuale
        assert all("Hide" in p["title"] or "Hide" in p["description"] for p in data4["patterns"])
    
    def test_error_handling_invalid_parameters(self, client, user_token):
        """Verifica la gestione di parametri non validi."""
        # Arrange
        headers = {"Authorization": f"Bearer {user_token}"}
        
        # Act - Parametro limit non valido
        response1 = client.get("/api/patterns/?limit=invalid", headers=headers)
        
        # Act - Parametro skip non valido
        response2 = client.get("/api/patterns/?skip=invalid", headers=headers)
        
        # Act - Parametro limit fuori range
        response3 = client.get("/api/patterns/?limit=1000", headers=headers)
        
        # Assert
        assert response1.status_code == 422  # Unprocessable Entity
        assert response2.status_code == 422  # Unprocessable Entity
        assert response3.status_code == 422  # Unprocessable Entity o 400 Bad Request
        
        # Verifica formato errori
        assert "detail" in response1.json()
        assert "detail" in response2.json()
        assert "detail" in response3.json()