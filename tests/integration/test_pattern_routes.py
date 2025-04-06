# tests/integration/test_pattern_routes.py
"""
Test di integrazione per le rotte API relative ai Privacy Patterns.

Verifica il funzionamento corretto degli endpoint REST, includendo
casi limite, paginazione, e varie combinazioni di parametri.
"""
from fastapi.testclient import TestClient
import pytest
import json
import re
from typing import List, Dict, Any

from src.models.privacy_pattern import PrivacyPattern
from src.models.gdpr_model import GDPRArticle
from src.models.pbd_principle import PbDPrinciple


class TestPatternRoutes:
    """Test completi per le rotte dei Privacy Pattern."""
    
    def test_get_patterns_no_auth(self, client):
        """Verifica che l'elenco dei pattern richieda autenticazione."""
        # Act
        response = client.get("/api/patterns/")
        
        # Assert
        assert response.status_code == 401
        assert "detail" in response.json()
        assert "autenticazione" in response.json()["detail"].lower() or "token" in response.json()["detail"].lower()
    
    def test_get_patterns_with_auth(self, client, user_token, db_session):
        """Verifica che un utente autenticato possa ottenere l'elenco dei pattern."""
        # Arrange
        headers = {"Authorization": f"Bearer {user_token}"}
        
        # Act
        response = client.get("/api/patterns/", headers=headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "patterns" in data
        assert "total" in data
        assert "page" in data
        assert "pages" in data
        
        # Verifica struttura dati
        if data["patterns"]:
            pattern = data["patterns"][0]
            required_fields = ["id", "title", "description", "strategy", "mvc_component"]
            for field in required_fields:
                assert field in pattern, f"Campo '{field}' mancante nel pattern"
    
    def test_get_patterns_pagination(self, client, user_token, db_session):
        """Verifica funzionalità di paginazione nell'elenco dei pattern."""
        # Creare abbastanza pattern per testare la paginazione
        for i in range(15):
            db_session.add(PrivacyPattern(
                title=f"Pagination Test Pattern {i}",
                description=f"Description for test {i}",
                context=f"Context {i}",
                problem=f"Problem {i}",
                solution=f"Solution {i}",
                consequences=f"Consequences {i}",
                strategy="Pagination",
                mvc_component="Model",
                created_by_id=1
            ))
        db_session.commit()
        
        # Arrange
        headers = {"Authorization": f"Bearer {user_token}"}
        
        # Test prima pagina (default)
        response1 = client.get("/api/patterns/?limit=5", headers=headers)
        
        assert response1.status_code == 200
        data1 = response1.json()
        assert len(data1["patterns"]) <= 5
        
        # Test seconda pagina
        response2 = client.get("/api/patterns/?skip=5&limit=5", headers=headers)
        
        assert response2.status_code == 200
        data2 = response2.json()
        assert len(data2["patterns"]) <= 5
        
        # Verifica che le pagine contengano pattern diversi
        page1_ids = [p["id"] for p in data1["patterns"]]
        page2_ids = [p["id"] for p in data2["patterns"]]
        assert set(page1_ids) != set(page2_ids), "Le pagine dovrebbero contenere pattern diversi"
        
        # Verifica informazioni di paginazione
        assert data1["page"] == 1
        assert data2["page"] == 2
        assert data1["size"] == 5
        assert data2["size"] == 5
        assert data1["total"] == data2["total"]
        assert data1["pages"] == data2["pages"]
    
    def test_get_patterns_with_filters(self, client, user_token, db_session):
        """Verifica il filtraggio dei pattern."""
        # Creare pattern con diverse strategie
        test_strategies = ["Minimize", "Hide", "Inform"]
        test_components = ["Model", "View", "Controller"]
        
        for i, (strategy, component) in enumerate(zip(test_strategies, test_components)):
            db_session.add(PrivacyPattern(
                title=f"Filter Test Pattern {i}",
                description=f"Description for {strategy} strategy",
                context=f"Context for {component}",
                problem=f"Problem {i}",
                solution=f"Solution {i}",
                consequences=f"Consequences {i}",
                strategy=strategy,
                mvc_component=component,
                created_by_id=1
            ))
        db_session.commit()
        
        # Arrange
        headers = {"Authorization": f"Bearer {user_token}"}
        
        # Test filtro per strategia
        for strategy in test_strategies:
            response = client.get(f"/api/patterns/?strategy={strategy}", headers=headers)
            
            assert response.status_code == 200
            data = response.json()
            
            # Verifica che tutti i pattern restituiti abbiano la strategia richiesta
            if data["patterns"]:
                assert all(p["strategy"] == strategy for p in data["patterns"]), f"Filtro per strategia {strategy} non funziona correttamente"
        
        # Test filtro per componente MVC
        for component in test_components:
            response = client.get(f"/api/patterns/?mvc_component={component}", headers=headers)
            
            assert response.status_code == 200
            data = response.json()
            
            # Verifica che tutti i pattern restituiti abbiano il componente richiesto
            if data["patterns"]:
                assert all(p["mvc_component"] == component for p in data["patterns"]), f"Filtro per componente {component} non funziona correttamente"
        
        # Test filtri combinati
        response = client.get(f"/api/patterns/?strategy={test_strategies[0]}&mvc_component={test_components[0]}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        if data["patterns"]:
            for pattern in data["patterns"]:
                assert pattern["strategy"] == test_strategies[0]
                assert pattern["mvc_component"] == test_components[0]
    
    def test_get_patterns_search(self, client, user_token, db_session):
        """Verifica la ricerca testuale nell'elenco dei pattern."""
        # Creare pattern con stringhe specifiche per test
        unique_strings = [
            "UniqueString123",
            "AnotherUniquePhrase456",
            "YetAnotherUniqueKeyword789"
        ]
        
        for i, unique_string in enumerate(unique_strings):
            db_session.add(PrivacyPattern(
                title=f"Search Test Pattern with {unique_string}",
                description=f"Description containing {unique_string} for test",
                context=f"Context {i}",
                problem=f"Problem {i}",
                solution=f"Solution {i}",
                consequences=f"Consequences {i}",
                strategy="Search",
                mvc_component="Model",
                created_by_id=1
            ))
        db_session.commit()
        
        # Arrange
        headers = {"Authorization": f"Bearer {user_token}"}
        
        # Test ricerca testuale
        for unique_string in unique_strings:
            response = client.get(f"/api/patterns/?search={unique_string}", headers=headers)
            
            assert response.status_code == 200
            data = response.json()
            
            # Verifica che la ricerca trovi il pattern con la stringa specifica
            assert data["total"] >= 1, f"La ricerca per {unique_string} non ha trovato risultati"
            
            found = False
            for pattern in data["patterns"]:
                if unique_string in pattern["title"] or unique_string in pattern["description"]:
                    found = True
                    break
            
            assert found, f"Pattern con {unique_string} non trovato nei risultati"
    
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
        assert "detail" in response.json()
        assert "autenticazione" in response.json()["detail"].lower() or "token" in response.json()["detail"].lower()
    
    def test_create_pattern_with_auth(self, client, user_token, db_session):
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
        
        # Verifica che il pattern sia stato effettivamente salvato
        pattern_id = data["id"]
        get_response = client.get(f"/api/patterns/{pattern_id}", headers=headers)
        assert get_response.status_code == 200
        assert get_response.json()["id"] == pattern_id
    
    def test_create_pattern_with_relations(self, client, user_token, db_session):
        """Verifica creazione pattern con relazioni a GDPR, PbD e vulnerabilità."""
        # Prepara dati relazionali
        gdpr_article = GDPRArticle(
            number="99",
            title="Test Article",
            content="Test content",
            summary="Test summary",
            category="Test"
        )
        db_session.add(gdpr_article)
        
        pbd_principle = PbDPrinciple(
            name="Test Principle",
            description="Test description",
            guidance="Test guidance"
        )
        db_session.add(pbd_principle)
        db_session.commit()
        
        # Arrange
        headers = {"Authorization": f"Bearer {user_token}"}
        pattern_data = {
            "title": "Pattern With Relations",
            "description": "Test pattern with relations",
            "context": "Test context with relations",
            "problem": "Test problem with relations",
            "solution": "Test solution with relations",
            "consequences": "Test consequences with relations",
            "strategy": "TestRelations",
            "mvc_component": "Model",
            "gdpr_ids": [gdpr_article.id],
            "pbd_ids": [pbd_principle.id],
            "vulnerability_ids": []
        }
        
        # Act
        response = client.post("/api/patterns/", json=pattern_data, headers=headers)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        
        # Verifica relazioni
        assert "gdpr_articles" in data
        assert len(data["gdpr_articles"]) == 1
        assert data["gdpr_articles"][0]["id"] == gdpr_article.id
        
        assert "pbd_principles" in data
        assert len(data["pbd_principles"]) == 1
        assert data["pbd_principles"][0]["id"] == pbd_principle.id
    
    def test_create_pattern_validation(self, client, user_token, db_session):
        """Verifica validazione nella creazione di pattern."""
        # Arrange
        headers = {"Authorization": f"Bearer {user_token}"}
        
        # Casi di test con dati invalidi
        invalid_cases = [
            # Titolo mancante
            {
                "description": "Test description",
                "context": "Test context",
                "problem": "Test problem",
                "solution": "Test solution",
                "consequences": "Test consequences",
                "strategy": "Test",
                "mvc_component": "Model"
            },
            # Descrizione mancante
            {
                "title": "Test Pattern",
                "context": "Test context",
                "problem": "Test problem",
                "solution": "Test solution",
                "consequences": "Test consequences",
                "strategy": "Test",
                "mvc_component": "Model"
            },
            # Strategia mancante
            {
                "title": "Test Pattern",
                "description": "Test description",
                "context": "Test context",
                "problem": "Test problem",
                "solution": "Test solution",
                "consequences": "Test consequences",
                "mvc_component": "Model"
            },
        ]
        
        for i, test_case in enumerate(invalid_cases):
            # Act
            response = client.post("/api/patterns/", json=test_case, headers=headers)
            
            # Assert
            assert response.status_code == 422, f"Caso {i} dovrebbe generare errore di validazione"
            assert "detail" in response.json(), f"Caso {i} dovrebbe contenere dettagli errore"
    
    def test_update_pattern(self, client, user_token, db_session):
        """Verifica che un utente possa aggiornare un pattern esistente."""
        # Creare un pattern da aggiornare
        pattern = PrivacyPattern(
            title="Original Pattern",
            description="Original description",
            context="Original context",
            problem="Original problem",
            solution="Original solution",
            consequences="Original consequences",
            strategy="Original",
            mvc_component="Model",
            created_by_id=1
        )
        db_session.add(pattern)
        db_session.commit()
        
        # Arrange
        headers = {"Authorization": f"Bearer {user_token}"}
        pattern_id = pattern.id
        
        update_data = {
            "title": "Updated Pattern",
            "description": "Updated description",
            "strategy": "Updated"
        }
        
        # Act
        response = client.put(f"/api/patterns/{pattern_id}", json=update_data, headers=headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        # Verifica campi aggiornati
        assert data["title"] == "Updated Pattern"
        assert data["description"] == "Updated description"
        assert data["strategy"] == "Updated"
        
        # Verifica che i campi non aggiornati rimangano invariati
        assert data["context"] == "Original context"
        assert data["problem"] == "Original problem"
        assert data["solution"] == "Original solution"
        
        # Verifica che l'aggiornamento sia persistente
        get_response = client.get(f"/api/patterns/{pattern_id}", headers=headers)
        updated_data = get_response.json()
        assert updated_data["title"] == "Updated Pattern"
    
    def test_update_nonexistent_pattern(self, client, user_token):
        """Verifica l'aggiornamento di un pattern inesistente."""
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
        assert "detail" in response.json()
        assert "non trovato" in response.json()["detail"].lower()
    
    def test_delete_pattern(self, client, admin_token, db_session):
        """Verifica che un admin possa eliminare un pattern."""
        # Creare un pattern da eliminare
        pattern = PrivacyPattern(
            title="Pattern To Delete",
            description="This pattern will be deleted",
            context="Delete context",
            problem="Delete problem",
            solution="Delete solution",
            consequences="Delete consequences",
            strategy="Delete",
            mvc_component="Model",
            created_by_id=1
        )
        db_session.add(pattern)
        db_session.commit()
        
        # Arrange
        headers = {"Authorization": f"Bearer {admin_token}"}
        pattern_id = pattern.id
        
        # Act
        response = client.delete(f"/api/patterns/{pattern_id}", headers=headers)
        
        # Assert
        assert response.status_code == 204
        
        # Verifica che il pattern non esista più
        get_response = client.get(f"/api/patterns/{pattern_id}", headers=headers)
        assert get_response.status_code == 404
    
    def test_get_patterns_by_strategy(self, client, user_token, db_session):
        """Verifica il raggruppamento dei pattern per strategia."""
        # Creare pattern con diverse strategie
        test_strategies = ["StrategyA", "StrategyB", "StrategyC"]
        
        for i, strategy in enumerate(test_strategies):
            # Crea più pattern per strategia per verificare il raggruppamento
            for j in range(2):
                db_session.add(PrivacyPattern(
                    title=f"{strategy} Pattern {j}",
                    description=f"Description for {strategy}",
                    context=f"Context for {strategy}",
                    problem=f"Problem {j}",
                    solution=f"Solution {j}",
                    consequences=f"Consequences {j}",
                    strategy=strategy,
                    mvc_component="Model",
                    created_by_id=1
                ))
        db_session.commit()
        
        # Arrange
        headers = {"Authorization": f"Bearer {user_token}"}
        
        # Act
        response = client.get("/api/patterns/by-strategy/StrategyA", headers=headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        # Verifica formato risultati e filtraggio per strategia
        assert isinstance(data, list)
        assert len(data) > 0
        assert all(p["strategy"] == "StrategyA" for p in data)
    
    def test_get_patterns_by_mvc(self, client, user_token, db_session):
        """Verifica il raggruppamento dei pattern per componente MVC."""
        # Creare pattern con diversi componenti MVC
        test_components = ["Model", "View", "Controller"]
        
        for i, component in enumerate(test_components):
            # Crea più pattern per componente per verificare il raggruppamento
            for j in range(2):
                db_session.add(PrivacyPattern(
                    title=f"{component} Pattern {j}",
                    description=f"Description for {component}",
                    context=f"Context for {component}",
                    problem=f"Problem {j}",
                    solution=f"Solution {j}",
                    consequences=f"Consequences {j}",
                    strategy="MVC",
                    mvc_component=component,
                    created_by_id=1
                ))
        db_session.commit()
        
        # Arrange
        headers = {"Authorization": f"Bearer {user_token}"}
        
        # Act
        response = client.get("/api/patterns/by-mvc/Model", headers=headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        # Verifica formato risultati e filtraggio per componente MVC
        assert isinstance(data, list)
        assert len(data) > 0
        assert all(p["mvc_component"] == "Model" for p in data)
    
    def test_get_related_patterns(self, client, user_token, db_session):
        """Verifica il recupero dei pattern correlati."""
        # Creare pattern correlati
        # Base pattern
        base_pattern = PrivacyPattern(
            title="Base Pattern",
            description="Base pattern for related test",
            context="Base context",
            problem="Base problem",
            solution="Base solution",
            consequences="Base consequences",
            strategy="RelatedTest",
            mvc_component="Model",
            created_by_id=1
        )
        db_session.add(base_pattern)
        
        # Pattern correlati (stessa strategia)
        for i in range(3):
            db_session.add(PrivacyPattern(
                title=f"Related Pattern {i}",
                description=f"Description for related pattern {i}",
                context=f"Context {i}",
                problem=f"Problem {i}",
                solution=f"Solution {i}",
                consequences=f"Consequences {i}",
                strategy="RelatedTest",  # Stessa strategia
                mvc_component="Model" if i % 2 == 0 else "View",
                created_by_id=1
            ))
        
        # Pattern non correlati (strategia diversa)
        for i in range(2):
            db_session.add(PrivacyPattern(
                title=f"Unrelated Pattern {i}",
                description=f"Description for unrelated pattern {i}",
                context=f"Context {i}",
                problem=f"Problem {i}",
                solution=f"Solution {i}",
                consequences=f"Consequences {i}",
                strategy="DifferentStrategy",  # Strategia diversa
                mvc_component="Model",
                created_by_id=1
            ))
        
        db_session.commit()
        
        # Arrange
        headers = {"Authorization": f"Bearer {user_token}"}
        pattern_id = base_pattern.id
        
        # Act
        response = client.get(f"/api/patterns/{pattern_id}/related", headers=headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        # Verifica formato risultati
        assert isinstance(data, list)
        
        # Verifica che i pattern correlati abbiano la stessa strategia
        assert all(p["strategy"] == "RelatedTest" for p in data)
        
        # Verifica che il pattern di base non sia tra i correlati
        assert all(p["id"] != pattern_id for p in data)
    
    def test_pattern_operations_edge_cases(self, client, user_token, db_session):
        """Verifica casi limite nelle operazioni sui pattern."""
        # Arrange
        headers = {"Authorization": f"Bearer {user_token}"}
        
        # Caso 1: Creazione con titolo molto lungo (limite 255 caratteri)
        long_title = "A" * 256  # Un carattere oltre il limite
        pattern_data = {
            "title": long_title,
            "description": "Test description",
            "context": "Test context",
            "problem": "Test problem",
            "solution": "Test solution",
            "consequences": "Test consequences",
            "strategy": "Test",
            "mvc_component": "Model"
        }
        
        response = client.post("/api/patterns/", json=pattern_data, headers=headers)
        assert response.status_code == 422, "Dovrebbe fallire con titolo troppo lungo"
        
        # Caso 2: Creazione con titolo duplicato
        duplicate_title = "Duplicate Title Pattern"
        
        # Prima creazione
        pattern_data["title"] = duplicate_title
        response1 = client.post("/api/patterns/", json=pattern_data, headers=headers)
        assert response1.status_code == 201
        
        # Seconda creazione con stesso titolo
        response2 = client.post("/api/patterns/", json=pattern_data, headers=headers)
        assert response2.status_code == 400, "Dovrebbe fallire con titolo duplicato"
        assert "già esistente" in response2.json()["detail"]
        
        # Caso 3: Aggiornamento con campo obbligatorio a valore vuoto
        pattern_id = response1.json()["id"]
        update_data = {
            "description": ""  # Valore vuoto
        }
        
        response = client.put(f"/api/patterns/{pattern_id}", json=update_data, headers=headers)
        assert response.status_code == 422, "Dovrebbe fallire con campo obbligatorio vuoto"