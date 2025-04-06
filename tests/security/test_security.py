# tests/security/test_security.py
"""
Test di sicurezza per l'applicazione.
"""
import pytest
import re
from fastapi.testclient import TestClient
import json
from typing import Dict, Any, List

@pytest.mark.security
class TestSecurity:
    """Test di sicurezza per l'applicazione."""
    
    def test_sql_injection_resistance(self, client, user_token):
        """Verifica la resistenza a SQL injection."""
        headers = {"Authorization": f"Bearer {user_token}"}
        
        # Lista di payload SQL injection
        sql_payloads = [
            "1' OR '1'='1",
            "1; DROP TABLE users; --",
            "' OR 1=1 --",
            "'; SELECT * FROM users; --",
            "1' UNION SELECT 1,username,password FROM users --"
        ]
        
        for payload in sql_payloads:
            # Test su endpoint di ricerca
            response = client.get(f"/api/search/patterns?q={payload}", headers=headers)
            assert response.status_code in [200, 404, 422], f"SQL injection may be possible with payload: {payload}"
            
            # Test su endpoint di pattern
            response = client.get(f"/api/patterns/{payload}", headers=headers)
            assert response.status_code in [404, 422], f"SQL injection may be possible with payload: {payload}"
    
    def test_xss_protection(self, client, admin_token):
        """Verifica la protezione da XSS (Cross-Site Scripting)."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # XSS payloads
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src='x' onerror='alert(\"XSS\")'>",
            "<body onload='alert(\"XSS\")'>",
            "';alert('XSS');//"
        ]
        
        # Crea pattern con payload XSS
        for payload in xss_payloads:
            pattern_data = {
                "title": f"Test Pattern {payload}",
                "description": f"Description {payload}",
                "context": f"Context {payload}",
                "problem": f"Problem {payload}",
                "solution": f"Solution {payload}",
                "consequences": f"Consequences {payload}",
                "strategy": "TestStrategy",
                "mvc_component": "Model"
            }
            
            # Tenta di creare un pattern con payload XSS
            response = client.post("/api/patterns/", json=pattern_data, headers=headers)
            
            # Il server dovrebbe accettare ma sanitizzare l'input
            if response.status_code == 201:
                pattern_id = response.json()["id"]
                
                # Recupera il pattern per verificare che il payload sia stato sanitizzato
                get_response = client.get(f"/api/patterns/{pattern_id}", headers=headers)
                assert get_response.status_code == 200
                
                pattern = get_response.json()
                
                # Verifica che i tag script siano stati rimossi o escapati
                assert "<script>" not in pattern["title"]
                assert "<script>" not in pattern["description"]
                
                # Cleanup
                client.delete(f"/api/patterns/{pattern_id}", headers=headers)
    
    def test_authentication_headers(self, client):
        """Verifica che gli header di autenticazione siano adeguatamente protetti."""
        response = client.get("/api/health")
        
        # Verifica la presenza di header di sicurezza
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers
        assert "Content-Security-Policy" in response.headers or "Content-Security-Policy-Report-Only" in response.headers
        
        # Verifica le impostazioni di sicurezza
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") in ["DENY", "SAMEORIGIN"]
    
    def test_rate_limiting(self, client):
        """Verifica che il rate limiting funzioni correttamente."""
        # Esegui molte richieste in poco tempo
        num_requests = 60
        responses = []
        
        for _ in range(num_requests):
            response = client.get("/api/health")
            responses.append(response)
        
        # Dovremmo vedere almeno un 429 (Too Many Requests) se il rate limiting è attivo
        status_codes = [r.status_code for r in responses]
        assert 429 in status_codes, "Rate limiting non sembra essere attivo"
        
        # Verifica la presenza dell'header di rate limit
        rate_limit_headers = ["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"]
        
        for header in rate_limit_headers:
            assert any(header in r.headers for r in responses), f"Header di rate limit '{header}' non trovato"