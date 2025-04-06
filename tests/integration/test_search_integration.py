# tests/integration/test_search_integration.py
"""
Test di integrazione per le funzionalità di ricerca.

Verifica l'interazione tra SearchService, SearchController e API endpoints.
Include test completi per ricerca con filtri multipli, paginazione e casi limite.
"""
import pytest
import json
import time
import statistics
import logging
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from src.services.search_service import SearchService
from src.controllers.search_controller import SearchController
from src.models.privacy_pattern import PrivacyPattern

logger = logging.getLogger(__name__)

@pytest.mark.integration
class TestSearchIntegration:
    """Test di integrazione per ricerca."""
    
    def test_search_api_with_elasticsearch(self, client, user_token, mock_elasticsearch, test_patterns):
        """Verifica API di ricerca con Elasticsearch."""
        # Configura mock per simulare risultati
        mock_elasticsearch.search.return_value = {
            "hits": {
                "total": {"value": 2},
                "hits": [
                    {
                        "_id": "1",
                        "_score": 1.5,
                        "_source": {
                            "id": 1,
                            "title": "Test Pattern 1",
                            "description": "Description 1",
                            "strategy": "Minimize",
                            "mvc_component": "Model",
                            "created_at": "2023-01-01T00:00:00",
                            "updated_at": "2023-01-01T00:00:00"
                        }
                    },
                    {
                        "_id": "2",
                        "_score": 1.2,
                        "_source": {
                            "id": 2,
                            "title": "Test Pattern 2",
                            "description": "Description 2",
                            "strategy": "Hide",
                            "mvc_component": "View",
                            "created_at": "2023-01-01T00:00:00",
                            "updated_at": "2023-01-01T00:00:00"
                        }
                    }
                ]
            }
        }
        
        # Esegui richiesta API
        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.get("/api/search/patterns?q=test&strategy=Minimize", headers=headers)
        
        # Verifica risposta
        assert response.status_code == 200
        data = response.json()
        
        # Verifica dati
        assert "total" in data
        assert "results" in data
        assert data["total"] == 2
        assert len(data["results"]) == 2
        
        # Verifica chiamata ES corretta
        mock_elasticsearch.search.assert_called_once()
        search_args = mock_elasticsearch.search.call_args[1]
        assert "body" in search_args
        
        # Verifica filtri applicati
        body = search_args["body"]
        assert "query" in body
        assert "bool" in body["query"]
        
        # Verifica che il filtro di strategia sia applicato
        filter_clauses = body["query"]["bool"].get("filter", [])
        assert any(clause.get("term", {}).get("strategy") == "Minimize" for clause in filter_clauses)
        
        # Verifica contenuto risposta
        assert data["results"][0]["title"] == "Test Pattern 1"
        assert data["results"][0]["strategy"] == "Minimize"
    
    def test_search_api_fallback_to_db(self, client, user_token, db_session, test_patterns):
        """Verifica fallback a ricerca DB quando ES non disponibile."""
        # Forza fallback a DB simulando ES non disponibile
        with patch.object(SearchService, "es", None):
            # Esegui richiesta API
            headers = {"Authorization": f"Bearer {user_token}"}
            response = client.get("/api/search/patterns?search=Minimize", headers=headers)
            
            # Verifica risposta
            assert response.status_code == 200
            data = response.json()
            
            # Verifica risultati
            assert "total" in data
            assert "results" in data
            assert data["total"] >= 1  # Dovrebbe trovare almeno il pattern con strategia "Minimize"
            
            # Verifica che i risultati contengano il pattern con strategia "Minimize"
            minimize_patterns = [p for p in data["results"] if "Minimize" in p["title"] or "Minimize" in p["description"] or p["strategy"] == "Minimize"]
            assert len(minimize_patterns) >= 1
    
    def test_search_with_multiple_filters(self, client, user_token, db_session, test_patterns):
        """Verifica ricerca con filtri multipli."""
        # Crea pattern con attributi specifici per il test
        from src.models.gdpr_model import GDPRArticle
        from src.models.pbd_principle import PbDPrinciple
        
        # Assicura che esistano articoli GDPR e principi PbD
        gdpr_article = db_session.query(GDPRArticle).first()
        if not gdpr_article:
            gdpr_article = GDPRArticle(
                number="5.1.c",
                title="Data Minimization",
                content="Personal data shall be adequate, relevant and limited",
                summary="Collect only necessary data"
            )
            db_session.add(gdpr_article)
            db_session.commit()
        
        pbd_principle = db_session.query(PbDPrinciple).first()
        if not pbd_principle:
            pbd_principle = PbDPrinciple(
                name="Privacy by Default",
                description="Maximum privacy by default",
                guidance="Configure systems with privacy by default"
            )
            db_session.add(pbd_principle)
            db_session.commit()
        
        # Associa il primo pattern con questi attributi
        test_pattern = test_patterns[0]
        test_pattern.gdpr_articles.append(gdpr_article)
        test_pattern.pbd_principles.append(pbd_principle)
        db_session.commit()
        
        # Esegui ricerca con filtri multipli
        headers = {"Authorization": f"Bearer {user_token}"}
        url = f"/api/search/patterns?gdpr_id={gdpr_article.id}&pbd_id={pbd_principle.id}&strategy={test_pattern.strategy}"
        response = client.get(url, headers=headers)
        
        # Verifica risposta
        assert response.status_code == 200
        data = response.json()
        
        # Verifica che i risultati rispettino i filtri
        assert data["total"] >= 1, "Dovrebbe esserci almeno un risultato con i filtri specificati"
        
        # Verifica che il pattern associato sia nei risultati
        result_ids = [p["id"] for p in data["results"]]
        assert test_pattern.id in result_ids, f"Pattern {test_pattern.id} non trovato nei risultati {result_ids}"
    
    def test_search_pagination(self, client, user_token, db_session, test_patterns):
        """Verifica funzionalità di paginazione nella ricerca."""
        # Crea una serie di pattern per garantire multipli risultati
        for i in range(15):  # Crea abbastanza pattern per testare paginazione
            db_session.add(PrivacyPattern(
                title=f"Pagination Test Pattern {i}",
                description=f"Description for pagination test {i}",
                context=f"Context {i}",
                problem=f"Problem {i}",
                solution=f"Solution {i}",
                consequences=f"Consequences {i}",
                strategy="Test",
                mvc_component="Model",
                created_by_id=1  # Assumendo che l'ID 1 esista nel database di test
            ))
        db_session.commit()
        
        # Test prima pagina
        headers = {"Authorization": f"Bearer {user_token}"}
        response_page1 = client.get("/api/search/patterns?strategy=Test&from_pos=0&size=5", headers=headers)
        
        assert response_page1.status_code == 200
        data_page1 = response_page1.json()
        
        assert len(data_page1["results"]) <= 5
        assert data_page1["total"] >= 15
        
        # Test seconda pagina
        response_page2 = client.get("/api/search/patterns?strategy=Test&from_pos=5&size=5", headers=headers)
        
        assert response_page2.status_code == 200
        data_page2 = response_page2.json()
        
        assert len(data_page2["results"]) <= 5
        
        # Verifica che le pagine siano diverse
        if data_page1["results"] and data_page2["results"]:
            page1_ids = [p["id"] for p in data_page1["results"]]
            page2_ids = [p["id"] for p in data_page2["results"]]
            assert set(page1_ids).isdisjoint(set(page2_ids)), "Le pagine dovrebbero contenere risultati diversi"
    
    def test_search_zero_results(self, client, user_token, db_session):
        """Verifica comportamento con zero risultati."""
        # Usa una query che sicuramente non darà risultati
        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.get("/api/search/patterns?q=ThisQueryWillNeverMatchAnything12345", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total"] == 0
        assert len(data["results"]) == 0
    
    def test_search_with_special_characters(self, client, user_token, db_session):
        """Verifica gestione caratteri speciali nella ricerca."""
        # Test con caratteri speciali che potrebbero causare problemi in query SQL o Elasticsearch
        headers = {"Authorization": f"Bearer {user_token}"}
        special_chars = ["'", "\"", ";", "--", "/*", "*/", "<script>", "%", "_"]
        
        for char in special_chars:
            response = client.get(f"/api/search/patterns?q={char}", headers=headers)
            assert response.status_code == 200, f"Ricerca con carattere '{char}' ha fallito"
            
            # Non verifichiamo il contenuto, solo che la richiesta non generi errori
    
    def test_reindex_all_patterns(self, client, admin_token, db_session, mock_elasticsearch, test_patterns):
        """Verifica funzionalità di reindicizzazione di tutti i pattern."""
        # Configura mock
        mock_elasticsearch.indices.exists.return_value = True
        mock_elasticsearch.indices.delete.return_value = {"acknowledged": True}
        mock_elasticsearch.indices.create.return_value = {"acknowledged": True}
        
        # Esegui richiesta reindicizzazione (solo admin)
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.post("/api/search/reindex", headers=headers)
        
        # Verifica risposta
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Reindicizzazione completata" in data["message"]
        
        # Verifica che l'indice sia stato ricreato
        mock_elasticsearch.indices.exists.assert_called()
        mock_elasticsearch.indices.create.assert_called()
        
        # Verifica che ogni pattern sia stato indicizzato
        assert mock_elasticsearch.index.call_count >= len(test_patterns)
        
        # Verifica indice corretto e format dati
        for call_args in mock_elasticsearch.index.call_args_list:
            assert call_args[1]["index"] == "privacy_patterns"
            assert "id" in call_args[1]["body"]
            assert "title" in call_args[1]["body"]
    
    def test_autocomplete_suggestions(self, client, user_token, mock_elasticsearch):
        """Verifica funzionalità di autocomplete."""
        # Configura mock per simulare suggestions
        mock_elasticsearch.search.return_value = {
            "hits": {
                "total": {"value": 2},
                "hits": [
                    {
                        "_id": "1",
                        "_score": 1.5,
                        "_source": {
                            "id": 1,
                            "title": "Minimize Data Collection",
                            "strategy": "Minimize",
                            "description": "Pattern for minimizing data collection"
                        },
                        "highlight": {
                            "title": ["<strong>Minimize</strong> Data Collection"],
                            "description": ["Pattern for <strong>minimizing</strong> data collection"]
                        }
                    },
                    {
                        "_id": "2",
                        "_score": 1.2,
                        "_source": {
                            "id": 2,
                            "title": "Minimal Disclosure",
                            "strategy": "Minimize",
                            "description": "Pattern for minimal disclosure of personal data"
                        },
                        "highlight": {
                            "title": ["<strong>Minimal</strong> Disclosure"],
                            "description": ["Pattern for <strong>minimal</strong> disclosure of personal data"]
                        }
                    }
                ]
            }
        }
        
        # Esegui richiesta
        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.get("/api/search/autocomplete?q=min", headers=headers)
        
        # Verifica risposta
        assert response.status_code == 200
        data = response.json()
        assert "suggestions" in data
        assert len(data["suggestions"]) == 2
        
        # Verifica contenuto
        for suggestion in data["suggestions"]:
            assert "min" in suggestion["text"].lower()
            assert "id" in suggestion
            assert "title" in suggestion
            assert "score" in suggestion
        
        # Verifica chiamata search corretta
        mock_elasticsearch.search.assert_called_once()
        search_args = mock_elasticsearch.search.call_args[1]
        assert "body" in search_args
        assert "size" in search_args["body"]
        assert "highlight" in search_args["body"]
    
    def test_search_performance_under_load(self, client, user_token, db_session, test_patterns):
        """Verifica performance di ricerca sotto carico."""
        # Crea ulteriori pattern per simulare carico
        for i in range(20):  # Numero sufficiente per test di carico
            db_session.add(PrivacyPattern(
                title=f"Load Test Pattern {i}",
                description=f"Description for load testing {i}",
                context=f"Context {i}",
                problem=f"Problem {i}",
                solution=f"Solution {i}",
                consequences=f"Consequences {i}",
                strategy="LoadTest",
                mvc_component="Model" if i % 3 == 0 else ("View" if i % 3 == 1 else "Controller"),
                created_by_id=1  # Assumendo che l'ID 1 esista nel database di test
            ))
        db_session.commit()
        
        # Esegui multiple ricerche in sequenza e misura tempi
        headers = {"Authorization": f"Bearer {user_token}"}
        search_queries = [
            "/api/search/patterns?strategy=LoadTest",
            "/api/search/patterns?mvc_component=Model",
            "/api/search/patterns?q=Load&strategy=LoadTest",
            "/api/search/patterns?q=Test&mvc_component=View"
        ]
        
        response_times = []
        for query in search_queries:
            start_time = time.time()
            response = client.get(query, headers=headers)
            end_time = time.time()
            
            assert response.status_code == 200
            response_times.append((end_time - start_time) * 1000)  # ms
        
        # Calcola statistiche
        avg_time = sum(response_times) / len(response_times)
        max_time = max(response_times)
        
        # Verifica performance accettabile
        assert avg_time < 500, f"Tempo medio di risposta troppo alto: {avg_time:.2f}ms"
        assert max_time < 1000, f"Tempo massimo di risposta troppo alto: {max_time:.2f}ms"
        
        # Log dei tempi per analisi
        logger.info(f"Tempi di ricerca sotto carico: media={avg_time:.2f}ms, max={max_time:.2f}ms")