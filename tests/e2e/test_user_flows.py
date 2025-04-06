# tests/e2e/test_user_flows.py
"""
Test end-to-end per flussi utente completi.

Verifica interazioni multi-step che attraversano diversi componenti del sistema.
"""
import pytest
import uuid
import time
import re
import json
from fastapi.testclient import TestClient

@pytest.mark.e2e
class TestUserFlows:
    """
    Test di flussi utente completi end-to-end.
    Richiede flag --run-e2e per essere eseguito.
    """
    
    @pytest.fixture(autouse=True)
    def skip_if_not_e2e(self, request):
        """Skip se non esplicitamente richiesto."""
        if not request.config.getoption("--run-e2e", default=False):
            pytest.skip("Salta test e2e (usa --run-e2e)")
    
    def test_user_registration_login_pattern_flow(self, client, db_session):
        """
        Test del flusso completo: registrazione, login e interazione con i pattern.
        """
        # PARTE 1: REGISTRAZIONE UTENTE
        # Genera dati utente unici
        test_email = f"test.{uuid.uuid4()}@example.com"
        test_username = f"testuser_{uuid.uuid4().hex[:8]}"
        test_password = "SecurePass123!"
        
        # Registra nuovo utente
        register_data = {
            "email": test_email,
            "username": test_username,
            "password": test_password,
            "full_name": "Test User"
        }
        
        register_response = client.post("/api/auth/register", json=register_data)
        assert register_response.status_code == 201, f"Registrazione fallita: {register_response.text}"
        
        # PARTE 2: LOGIN
        # Ottieni token JWT con le nuove credenziali
        login_data = {
            "username": test_email,  # OAuth2 usa username, ma noi usiamo email
            "password": test_password
        }
        
        login_response = client.post(
            "/api/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert login_response.status_code == 200
        token_data = login_response.json()
        assert "access_token" in token_data
        access_token = token_data["access_token"]
        
        # Verifica che il token sia valido ottenendo info utente
        headers = {"Authorization": f"Bearer {access_token}"}
        me_response = client.get("/api/auth/me", headers=headers)
        
        assert me_response.status_code == 200
        user_data = me_response.json()
        assert user_data["email"] == test_email
        assert user_data["username"] == test_username
        
        # PARTE 3: CREAZIONE PATTERN
        # Crea un nuovo pattern
        pattern_data = {
            "title": f"Test Pattern {uuid.uuid4().hex[:8]}",
            "description": "Pattern created during e2e test",
            "context": "E2E testing context",
            "problem": "Need to verify full user flow",
            "solution": "Create comprehensive E2E tests",
            "consequences": "Confident software releases",
            "strategy": "TestE2E",
            "mvc_component": "Model"
        }
        
        create_response = client.post("/api/patterns/", json=pattern_data, headers=headers)
        
        assert create_response.status_code == 201
        pattern = create_response.json()
        pattern_id = pattern["id"]
        
        # PARTE 4: RICERCA PATTERN
        # Ricerca il pattern appena creato
        search_response = client.get(f"/api/search/patterns?q=TestE2E", headers=headers)
        
        assert search_response.status_code == 200
        search_results = search_response.json()
        assert search_results["total"] >= 1
        
        # Verifica che il pattern creato sia nei risultati
        found = False
        for result in search_results["results"]:
            if result["id"] == pattern_id:
                found = True
                break
        
        assert found, "Pattern creato non trovato nei risultati di ricerca"
        
        # PARTE 5: AGGIORNA PATTERN
        # Aggiorna il pattern creato
        update_data = {
            "title": f"Updated E2E Pattern {uuid.uuid4().hex[:8]}",
            "description": "Pattern updated during e2e test",
            "strategy": "UpdatedE2E"
        }
        
        update_response = client.put(f"/api/patterns/{pattern_id}", json=update_data, headers=headers)
        
        assert update_response.status_code == 200
        updated_pattern = update_response.json()
        assert updated_pattern["title"] == update_data["title"]
        assert updated_pattern["description"] == update_data["description"]
        assert updated_pattern["strategy"] == update_data["strategy"]
        
        # PARTE 6: VISUALIZZA DETTAGLI PATTERN
        # Ottieni dettagli completi del pattern
        detail_response = client.get(f"/api/patterns/{pattern_id}", headers=headers)
        
        assert detail_response.status_code == 200
        pattern_details = detail_response.json()
        assert pattern_details["id"] == pattern_id
        assert pattern_details["title"] == update_data["title"]
        
        # PARTE 7: VISUALIZZA PATTERN CORRELATI
        # Verifica funzionalità pattern correlati
        related_response = client.get(f"/api/patterns/{pattern_id}/related", headers=headers)
        
        assert related_response.status_code == 200
        # Non verifichiamo i contenuti, solo che la richiesta abbia successo
        
        # PARTE 8: ELIMINA PATTERN
        # Elimina il pattern creato
        delete_response = client.delete(f"/api/patterns/{pattern_id}", headers=headers)
        
        assert delete_response.status_code == 204
        
        # Verifica che il pattern sia stato eliminato
        get_response = client.get(f"/api/patterns/{pattern_id}", headers=headers)
        assert get_response.status_code == 404
    
    def test_search_advanced_filters_flow(self, client, user_token, db_session):
        """
        Test del flusso di ricerca avanzata con filtri multipli.
        """
        headers = {"Authorization": f"Bearer {user_token}"}
        
        # Passo 1: Verifica disponibilità filtri
        # Ottieni pattern per identificare valori disponibili per i filtri
        patterns_response = client.get("/api/patterns/", headers=headers)
        assert patterns_response.status_code == 200
        
        patterns_data = patterns_response.json()
        assert "patterns" in patterns_data
        
        # Estrai valori unici per filtri (se esistono pattern)
        strategies = set()
        mvc_components = set()
        
        if patterns_data["patterns"]:
            for pattern in patterns_data["patterns"]:
                if "strategy" in pattern:
                    strategies.add(pattern["strategy"])
                if "mvc_component" in pattern:
                    mvc_components.add(pattern["mvc_component"])
        
        # Se non abbiamo valori dai pattern esistenti, usiamo valori predefiniti
        if not strategies:
            strategies = {"Minimize", "Inform", "Control"}
        if not mvc_components:
            mvc_components = {"Model", "View", "Controller"}
        
        # Passo 2: Esegui ricerca con un singolo filtro
        for strategy in strategies:
            search_response = client.get(f"/api/search/patterns?strategy={strategy}", headers=headers)
            assert search_response.status_code == 200
            
            search_data = search_response.json()
            assert "results" in search_data
            
            # Verifica che i risultati rispettino il filtro
            if search_data["results"]:
                for result in search_data["results"]:
                    assert result["strategy"] == strategy
        
        # Passo 3: Esegui ricerca con filtri multipli
        # Prendi il primo valore da ogni set di filtri
        strategy = next(iter(strategies))
        mvc_component = next(iter(mvc_components))
        
        combined_response = client.get(
            f"/api/search/patterns?strategy={strategy}&mvc_component={mvc_component}",
            headers=headers
        )
        assert combined_response.status_code == 200
        
        combined_data = combined_response.json()
        assert "results" in combined_data
        
        # Verifica che i risultati rispettino entrambi i filtri
        if combined_data["results"]:
            for result in combined_data["results"]:
                assert result["strategy"] == strategy
                assert result["mvc_component"] == mvc_component
        
        # Passo 4: Esegui ricerca con filtri e testo
        # Usa una query che probabilmente restituirà risultati basati sui dati di test
        text_search = "pattern"  # Termine generico che probabilmente esiste nei titoli
        
        text_filter_response = client.get(
            f"/api/search/patterns?q={text_search}&strategy={strategy}",
            headers=headers
        )
        assert text_filter_response.status_code == 200
        
        text_filter_data = text_filter_response.json()
        assert "results" in text_filter_data
        
        # Verifica che i risultati rispettino il filtro di strategia
        if text_filter_data["results"]:
            for result in text_filter_data["results"]:
                assert result["strategy"] == strategy
                
                # Il testo dovrebbe essere presente in almeno uno dei campi principali
                text_found = False
                for field in ["title", "description"]:
                    if field in result and text_search.lower() in result[field].lower():
                        text_found = True
                        break
                
                assert text_found or text_filter_data["total"] == 0, "Risultato non contiene il testo cercato"
        
        # Passo 5: Verifica paginazione
        pagination_response = client.get(
            f"/api/search/patterns?from_pos=0&size=5",
            headers=headers
        )
        assert pagination_response.status_code == 200
        
        pagination_data = pagination_response.json()
        assert "results" in pagination_data
        
        # Verifica che i risultati rispettino il limite di paginazione
        assert len(pagination_data["results"]) <= 5
        
        # Passo 6: Verifica seconda pagina
        if pagination_data["total"] > 5:
            page2_response = client.get(
                f"/api/search/patterns?from_pos=5&size=5",
                headers=headers
            )
            assert page2_response.status_code == 200
            
            page2_data = page2_response.json()
            assert "results" in page2_data
            
            # Verifica che i risultati della seconda pagina siano diversi dalla prima
            page1_ids = [r["id"] for r in pagination_data["results"]]
            page2_ids = [r["id"] for r in page2_data["results"]]
            
            # Dovrebbero essere insiemi disgiunti
            assert not set(page1_ids).intersection(set(page2_ids)), "Le pagine contengono risultati duplicati"
    
    def test_newsletter_subscription_flow(self, client):
        """
        Test del flusso di iscrizione alla newsletter.
        """
        # PARTE 1: ISCRIZIONE ALLA NEWSLETTER
        # Genera email unica
        test_email = f"newsletter_{uuid.uuid4()}@example.com"
        
        # Invia richiesta di iscrizione
        subscription_data = {
            "email": test_email
        }
        
        subscribe_response = client.post("/api/newsletter/subscribe", json=subscription_data)
        
        # L'API dovrebbe confermare l'iscrizione
        assert subscribe_response.status_code in [200, 201], f"Iscrizione fallita: {subscribe_response.text}"
        
        # PARTE 2: VERIFICA ISCRIZIONE
        # Dovrebbe esistere un endpoint per verificare lo stato dell'iscrizione
        if hasattr(client, 'get') and callable(getattr(client, 'get')):
            verify_response = client.get(f"/api/newsletter/status?email={test_email}")
            
            if verify_response.status_code == 200:
                status_data = verify_response.json()
                assert "subscribed" in status_data
                assert status_data["subscribed"] is True
        
        # PARTE 3: CANCELLAZIONE ISCRIZIONE
        # Dovrebbe esistere un endpoint per cancellare l'iscrizione
        if hasattr(client, 'delete') and callable(getattr(client, 'delete')):
            unsubscribe_response = client.delete(f"/api/newsletter/unsubscribe?email={test_email}")
            
            if unsubscribe_response.status_code == 200:
                # Verifica cancellazione
                if hasattr(client, 'get') and callable(getattr(client, 'get')):
                    verify_after_response = client.get(f"/api/newsletter/status?email={test_email}")
                    
                    if verify_after_response.status_code == 200:
                        status_after_data = verify_after_response.json()
                        assert "subscribed" in status_after_data
                        assert status_after_data["subscribed"] is False