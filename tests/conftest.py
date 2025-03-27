# tests/conftest.py
"""
Fixtures condivise per i test.

Questo modulo contiene fixture pytest riutilizzabili in diversi test.
"""
import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Aggiungi la directory principale al path per importare i moduli
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main import app
from src.db.session import get_db
from src.models.base import Base
from src.models.user_model import User, UserRole
from src.utils.password import get_password_hash
from src.utils.jwt import create_access_token


# Create an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """
    Fixture che fornisce una sessione di database di test.
    
    Crea un database in-memory fresco per ogni test.
    """
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create a new database session
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        
    # Drop all tables after the test
    Base.metadata.drop_all(bind=engine)


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
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("password123"),
        full_name="Test User",
        role=UserRole.EDITOR,
        is_active=True
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
    admin = User(
        email="admin@example.com",
        username="admin",
        hashed_password=get_password_hash("admin123"),
        full_name="Admin User",
        role=UserRole.ADMIN,
        is_active=True
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
    return create_access_token({"sub": test_user.id})


@pytest.fixture(scope="function")
def admin_token(test_admin):
    """
    Fixture che fornisce un token JWT per l'utente admin di test.
    """
    return create_access_token({"sub": test_admin.id})