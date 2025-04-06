# tests/services/test_newsletter_service.py
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from sqlalchemy.orm import Session

from src.services.newsletter_service import NewsletterService
from src.models.newsletter import NewsletterSubscription

@pytest.fixture
def newsletter_service():
    return NewsletterService()

@pytest.fixture
def db_session():
    # Mock della sessione database
    db = MagicMock(spec=Session)
    db.query.return_value.filter.return_value.first.return_value = None
    db.commit = MagicMock()
    return db

def test_subscribe_new_email(newsletter_service, db_session):
    """Test iscrizione con nuova email."""
    # Setup
    email = "nuovo.utente@example.com"
    
    # Simula l'email che non esiste
    db_session.query.return_value.filter.return_value.first.return_value = None
    
    # Patch della funzione di invio email
    with patch.object(newsletter_service, 'send_verification_email', return_value=True):
        # Chiamata alla funzione
        result = newsletter_service.subscribe(db_session, email)
    
    # Assertions
    assert result.get('success') is True
    assert "Iscrizione creata" in result.get('message', '')
    assert result.get('requires_verification') is True
    
    # Verifica che sia stato chiamato db.add con un'istanza di NewsletterSubscription
    assert db_session.add.called
    added_subscription = db_session.add.call_args[0][0]
    assert isinstance(added_subscription, NewsletterSubscription)
    assert added_subscription.email == email
    assert added_subscription.is_active is True
    assert added_subscription.is_verified is False
    assert added_subscription.verification_token is not None

def test_subscribe_existing_verified_email(newsletter_service, db_session):
    """Test iscrizione con email già verificata."""
    # Setup
    email = "utente.esistente@example.com"
    
    # Simula l'email che esiste e verificata
    existing_subscription = NewsletterSubscription(
        id=1, 
        email=email, 
        is_active=True, 
        is_verified=True,
        subscribed_at=datetime.utcnow()
    )
    db_session.query.return_value.filter.return_value.first.return_value = existing_subscription
    
    # Chiamata alla funzione
    result = newsletter_service.subscribe(db_session, email)
    
    # Assertions
    assert result.get('success') is False
    assert "Email già iscritta" in result.get('message', '')
    assert result.get('already_subscribed') is True
    
    # Verifica che non sia stato chiamato db.add
    assert not db_session.add.called

def test_subscribe_existing_unverified_email(newsletter_service, db_session):
    """Test iscrizione con email esistente ma non verificata."""
    # Setup
    email = "non.verificato@example.com"
    
    # Simula l'email che esiste ma non verificata
    existing_subscription = NewsletterSubscription(
        id=1, 
        email=email, 
        is_active=True, 
        is_verified=False,
        verification_token="old-token",
        subscribed_at=datetime.utcnow()
    )
    db_session.query.return_value.filter.return_value.first.return_value = existing_subscription
    
    # Patch della funzione di invio email
    with patch.object(newsletter_service, 'send_verification_email', return_value=True):
        # Chiamata alla funzione
        result = newsletter_service.subscribe(db_session, email)
    
    # Assertions
    assert result.get('success') is True
    assert "Nuova email di verifica inviata" in result.get('message', '')
    assert result.get('requires_verification') is True
    
    # Verifica che il token sia stato aggiornato
    assert existing_subscription.verification_token != "old-token"
    
    # Verifica che sia stato effettuato un commit
    assert db_session.commit.called

def test_unsubscribe_success(newsletter_service, db_session):
    """Test cancellazione iscrizione."""
    # Setup
    email = "iscritto@example.com"
    
    # Simula l'email che esiste
    existing_subscription = NewsletterSubscription(
        id=1, 
        email=email, 
        is_active=True, 
        is_verified=True,
        subscribed_at=datetime.utcnow()
    )
    db_session.query.return_value.filter.return_value.first.return_value = existing_subscription
    
    # Patch della funzione di invio email
    with patch.object(newsletter_service.email_service, 'send_email', return_value=True):
        # Chiamata alla funzione
        result = newsletter_service.unsubscribe(db_session, email)
    
    # Assertions
    assert result.get('success') is True
    assert "cancellata con successo" in result.get('message', '')
    
    # Verifica che is_active sia stato impostato a False
    assert existing_subscription.is_active is False
    
    # Verifica che sia stato effettuato un commit
    assert db_session.commit.called

def test_verify_subscription_success(newsletter_service, db_session):
    """Test verifica iscrizione con token valido."""
    # Setup
    email = "da.verificare@example.com"
    token = "valid-token"
    
    # Simula l'email con token valido
    subscription = NewsletterSubscription(
        id=1, 
        email=email, 
        is_active=True, 
        is_verified=False,
        verification_token=token,
        subscribed_at=datetime.utcnow()
    )
    db_session.query.return_value.filter.return_value.first.return_value = subscription
    
    # Patch della funzione di invio email
    with patch.object(newsletter_service, 'send_welcome_email', return_value=True):
        # Chiamata alla funzione
        result = newsletter_service.verify_subscription(db_session, email, token)
    
    # Assertions
    assert result.get('success') is True
    assert "verificata con successo" in result.get('message', '')
    
    # Verifica che is_verified sia True e token sia None
    assert subscription.is_verified is True
    assert subscription.verification_token is None
    
    # Verifica che sia stato effettuato un commit
    assert db_session.commit.called