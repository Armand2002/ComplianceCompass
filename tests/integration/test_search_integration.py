# tests/integration/test_search_integration.py
"""
Test di integrazione per le funzionalità di ricerca.

Verifica l'interazione tra SearchService, SearchController e API endpoints.
"""
import pytest
import json
import time
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from src.services.search_service import SearchService
from src.controllers.search_controller import SearchController
from src.models.privacy_pattern import PrivacyPattern

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
    
    def test_autocomplete_suggestions(self, client, user_token, mock_elasticsearch):
        """Verifica funzionalità di autocomplete."""
        # Configura mock per simulare suggestions
        mock_elasticsearch.search.return_value = {
            "suggest": {
                "pattern_suggest": [
                    {
                        "text": "min",
                        "offset": 0,
                        "length": 3,
                        "options": [
                            {
                                "text": "Minimize",
                                "_source": {"id": 1, "title": "Minimize Data Collection"}
                            },
                            {
                                "text": "Minimal Disclosure",
                                "_source": {"id": 2, "title": "Minimal Disclosure"}
                            }
                        ]
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
        assert len(data["suggestions"]) > 0
        
        # Verifica contenuto
        for suggestion in data["suggestions"]:
            assert "min" in suggestion["text"].lower()
    
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
        assert data["total"] >= 1
        assert test_pattern.id in [p["id"] for p in data["results"]]
    
    def test_search_performance(self, client, user_token, large_dataset):
        """
        Verifica performance di ricerca con dataset grande.
        Richiede flag --large-dataset per essere eseguito.
        """
        # Misura tempo per ricerca semplice
        headers = {"Authorization": f"Bearer {user_token}"}
        start_time = time.time()
        response1 = client.get("/api/search/patterns?q=Performance", headers=headers)
        simple_search_time = time.time() - start_time
        
        # Misura tempo per ricerca con filtri
        start_time = time.time()
        response2 = client.get("/api/search/patterns?q=Performance&strategy=Strategy 1&mvc_component=Model", headers=headers)
        filtered_search_time = time.time() - start_time
        
        # Verifica risposte
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verifica tempi di risposta accettabili
        assert simple_search_time < 1.0, f"Ricerca semplice troppo lenta: {simple_search_time:.2f}s"
        assert filtered_search_time < 1.5, f"Ricerca filtrata troppo lenta: {filtered_search_time:.2f}s"
        
        # Verifica risultati
        data1 = response1.json()
        data2 = response2.json()
        
        # La ricerca filtrata dovrebbe restituire meno risultati
        assert data1["total"] >= data2["total"]
        
        # Verifica paginazione
        assert "page" in data1
        assert "pages" in data1
        assert data1["pages"] > 1  # Dataset grande dovrebbe avere più di una pagina
    
    def test_search_api_elasticsearch_error(self, client, user_token, mock_elasticsearch):
        """Verifica gestione errori di Elasticsearch."""
        # Configura mock per simulare errore ES
        mock_elasticsearch.search.side_effect = Exception("Elasticsearch search error")
        
        # Esegui richiesta API
        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.get("/api/search/patterns?q=test", headers=headers)
        
        # Verifica risposta
        assert response.status_code == 200  # Dovrebbe comunque restituire 200, con info errore
        data = response.json()
        
        # Verifica formato risposta con errore
        assert "total" in data
        assert "results" in data
        assert "error" in data
        assert data["total"] == 0
        assert len(data["results"]) == 0
    
    def test_search_api_authentication(self, client):
        """Verifica che la ricerca richieda autenticazione."""
        # Esegui richiesta API senza token
        response = client.get("/api/search/patterns?q=test")
        
        # Verifica risposta
        assert response.status_code == 401  # Unauthorized