# tests/conftest.py
"""
Configurazioni e fixture condivise per i test.

Fornisce configurazioni globali e fixture riutilizzabili 
per l'intera suite di test.
"""

import os
import sys
from datetime import datetime
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Aggiungi la directory principale al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main import app
from src.db.session import get_db
from src.models.base import Base
from src.models.user_model import User, UserRole
from src.utils.password import get_password_hash
from src.utils.jwt import create_access_token
from src.services.elasticsearch_service import ElasticsearchService

# Configurazione del database di test
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def test_engine():
    """
    Crea un motore di database in-memory per i test.
    
    Returns:
        Engine: Motore database SQLAlchemy
    """
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    return engine

@pytest.fixture(scope="function")
def db(test_engine):
    """
    Fixture per una sessione database isolata per ogni test.
    
    Args:
        test_engine: Motore database di test
    
    Returns:
        Session: Sessione database isolata
    """
    # Crea le tabelle
    Base.metadata.create_all(bind=test_engine)
    
    # Crea una sessione
    SessionLocal = sessionmaker(
        autocommit=False, 
        autoflush=False, 
        bind=test_engine
    )
    session = SessionLocal()
    
    try:
        yield session
    finally:
        # Chiudi la sessione e rimuovi le tabelle
        session.close()
        Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(scope="function")
def client(db):
    """
    Fixture che fornisce un client di test per l'API.
    
    Override la dipendenza get_db per utilizzare il database di test.
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as client:
        yield client
    
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def test_user(db):
    """
    Fixture che crea un utente di test nel database.
    """
    # Verifica se l'utente esiste già
    user = db.query(User).filter(User.email == "test@example.com").first()
    if user:
        return user
    
    # Crea un nuovo utente di test
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("password123"),
        full_name="Test User",
        role=UserRole.EDITOR,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user

@pytest.fixture(scope="function")
def test_admin(db):
    """
    Fixture che crea un utente admin di test nel database.
    """
    # Verifica se l'admin esiste già
    admin = db.query(User).filter(User.email == "admin@example.com").first()
    if admin:
        return admin
    
    # Crea un nuovo admin di test
    admin = User(
        email="admin@example.com",
        username="admin",
        hashed_password=get_password_hash("admin123"),
        full_name="Admin User",
        role=UserRole.ADMIN,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    return admin

@pytest.fixture(scope="function")
def user_token(test_user):
    """
    Fixture che fornisce un token JWT per l'utente di test.
    """
    return create_access_token(data={"sub": test_user.id, "role": test_user.role.value})

@pytest.fixture(scope="function")
def admin_token(test_admin):
    """
    Fixture che fornisce un token JWT per l'utente admin di test.
    """
    return create_access_token(data={"sub": test_admin.id, "role": test_admin.role.value})

@pytest.fixture(scope="session")
def mock_elasticsearch():
    """
    Fixture per un servizio Elasticsearch mock.
    
    Returns:
        ElasticsearchService: Servizio Elasticsearch simulato
    """
    es_service = ElasticsearchService()
    # Assicura che sia disponibile per i test
    es_service.is_available = True
    return es_service

def pytest_configure(config):
    """
    Hook di configurazione pytest per impostazioni globali.
    
    Args:
        config: Configurazione pytest
    """
    # Imposta marker personalizzati
    config.addinivalue_line(
        "markers", 
        "integration: Contrassegna test di integrazione"
    )
    config.addinivalue_line(
        "markers", 
        "performance: Test di performance"
    )
    config.addinivalue_line(
        "markers", 
        "security: Test di sicurezza"
    )

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """
    Personalizza il sommario finale dei test.
    
    Args:
        terminalreporter: Reporter terminale
        exitstatus: Stato di uscita
        config: Configurazione pytest
    """
    # Stampa sommario personalizzato
    terminalreporter.write_line("\n--- Sommario Test Compliance Compass ---")
    
    # Counters
    passed = len(terminalreporter.stats.get('passed', []))
    failed = len(terminalreporter.stats.get('failed', []))
    skipped = len(terminalreporter.stats.get('skipped', []))
    
    terminalreporter.write_line(
        f"Test Passati: {passed}, "
        f"Falliti: {failed}, "
        f"Skippati: {skipped}"
    )