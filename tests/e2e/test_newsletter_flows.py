# tests/e2e/test_newsletter_flows.py
import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.main import app  # Importa l'istanza FastAPI
from src.models.newsletter import NewsletterSubscription

@pytest.mark.e2e
def test_newsletter_subscription_complete_flow():
    """Test del flusso completo di iscrizione, verifica e cancellazione newsletter."""
    client = TestClient(app)
    
    # FASE 1: ISCRIZIONE
    # Genera email unica
    test_email = f"test.newsletter.{uuid.uuid4()}@example.com"
    
    # Invia richiesta di iscrizione
    subscription_response = client.post(
        "/api/newsletter/subscribe", 
        json={"email": test_email}
    )
    
    # Verifica risposta e status code
    assert subscription_response.status_code == 201, f"Subscription failed: {subscription_response.text}"
    assert "requires_verification" in subscription_response.json()
    assert subscription_response.json()["requires_verification"] is True
    
    # FASE 2: RECUPERO TOKEN (simulato - in produzione arriva via email)
    # Questo richiede accesso diretto al DB che in un test E2E reale andrebbe fatto con un'API di admin
    with Session(app.state.engine) as db:
        subscription = db.query(NewsletterSubscription).filter(
            NewsletterSubscription.email == test_email
        ).first()
        
        assert subscription is not None, "Subscription not found in database"
        assert subscription.verification_token is not None, "Verification token not generated"
        
        verification_token = subscription.verification_token
    
    # FASE 3: VERIFICA ISCRIZIONE
    verify_response = client.post(
        f"/api/newsletter/verify?email={test_email}&token={verification_token}"
    )
    
    # Verifica risposta
    assert verify_response.status_code == 200, f"Verification failed: {verify_response.text}"
    assert "message" in verify_response.json()
    assert "verificata con successo" in verify_response.json()["message"]
    
    # FASE 4: VERIFICA STATO
    status_response = client.get(f"/api/newsletter/status?email={test_email}")
    
    # Verifica risposta
    assert status_response.status_code == 200
    status_data = status_response.json()
    assert status_data["subscribed"] is True
    assert status_data["is_verified"] is True
    assert status_data["is_active"] is True
    
    # FASE 5: CANCELLAZIONE
    unsubscribe_response = client.delete(f"/api/newsletter/unsubscribe?email={test_email}")
    
    # Verifica risposta
    assert unsubscribe_response.status_code == 200
    assert "message" in unsubscribe_response.json()
    assert "cancellata con successo" in unsubscribe_response.json()["message"]
    
    # FASE 6: VERIFICA CANCELLAZIONE
    status_after_response = client.get(f"/api/newsletter/status?email={test_email}")
    
    # Lo stato dovrebbe ancora mostrare iscritto ma con is_active = False
    assert status_after_response.status_code == 200
    status_after_data = status_after_response.json()
    assert status_after_data["subscribed"] is True
    assert status_after_data["is_active"] is False