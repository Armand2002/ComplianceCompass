"""
Configurazione centralizzata per i test di Compliance Compass.

Fornisce fixture condivise, mock e utilities per tutti i tipi di test.
"""
import os
import sys
import pytest
import logging
from typing import Dict, Any, Generator, List
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from sqlalchemy_utils import create_database, database_exists, drop_database

# Aggiungi la directory principale al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main import app
from src.db.session import get_db
from src.models.base import Base
from src.models.user_model import User, UserRole
from src.utils.password import get_password_hash
from src.utils.jwt import create_access_token

# Configurazione logging durante i test
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Configurazione del database di test
def get_test_db_url():
    """Restituisce l'URL del database di test."""
    if os.environ.get("CI") == "true":
        # Usa PostgreSQL in ambiente CI
        return "postgresql://postgres:postgres@localhost:5432/test_compliance_compass"
    else:
        # Usa SQLite in locale
        return "sqlite:///:memory:"

TEST_DATABASE_URL = get_test_db_url()

# Fixture per decidere se usare un DB reale o mocks
def pytest_addoption(parser):
    parser.addoption(
        "--use-mock-db", 
        action="store_true", 
        default=False,
        help="Usa database mock invece di un database reale"
    )

@pytest.fixture(scope="session")
def use_mock_db(request):
    return request.config.getoption("--use-mock-db")

# Fixture per il motore DB di test
@pytest.fixture(scope="session")
def test_engine(use_mock_db):
    """
    Crea un motore di database per i test.
    
    Args:
        use_mock_db: Se True, usa un mock invece di un DB reale
        
    Returns:
        Engine: Motore SQLAlchemy per i test
    """
    if use_mock_db:
        # Restituisci un mock engine
        mock_engine = MagicMock()
        mock_engine.dispose = MagicMock()
        return mock_engine
    
    if TEST_DATABASE_URL.startswith("postgresql"):
        # Crea database PostgreSQL se non esiste
        db_url = TEST_DATABASE_URL.rsplit("/", 1)[0]
        db_name = TEST_DATABASE_URL.rsplit("/", 1)[1]
        temp_url = f"{db_url}/postgres"
        engine = create_engine(temp_url)
        
        with engine.connect() as conn:
            conn.execute(f"DROP DATABASE IF EXISTS {db_name}")
            conn.execute(f"CREATE DATABASE {db_name}")
        
        engine = create_engine(
            TEST_DATABASE_URL,
            pool_pre_ping=True,
            echo=False
        )
    else:
        # SQLite in memoria
        engine = create_engine(
            TEST_DATABASE_URL,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=False
        )
    
    # Crea le tabelle
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Pulisci dopo i test
    if TEST_DATABASE_URL.startswith("postgresql"):
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
    
@pytest.fixture
def db_session(test_engine, use_mock_db) -> Generator[Session, None, None]:
    """
    Fornisce una sessione DB isolata per ogni test.
    
    Args:
        test_engine: Engine del database di test
        use_mock_db: Se usare un mock DB
        
    Yields:
        Session: Sessione SQLAlchemy per test
    """
    if use_mock_db:
        # Restituisci una sessione mock
        mock_session = MagicMock()
        mock_session.commit = MagicMock()
        mock_session.rollback = MagicMock()
        mock_session.close = MagicMock()
        yield mock_session
    else:
        # Crea sessione reale
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
        session = SessionLocal()
        
        # Inizia una transazione che verrà rollback dopo il test
        connection = test_engine.connect()
        transaction = connection.begin()
        
        yield session
        
        # Rollback alla fine del test
        session.close()
        transaction.rollback()
        connection.close()

@pytest.fixture
def client(db_session) -> Generator[TestClient, None, None]:
    """
    Fornisce un client HTTP per testare le API.
    
    Args:
        db_session: Sessione DB per i test
        
    Yields:
        TestClient: Client FastAPI per API testing
    """
    def _get_test_db():
        try:
            yield db_session
        finally:
            pass
    
    # Override la dipendenza get_db
    app.dependency_overrides[get_db] = _get_test_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Ripristina dependency originale
    app.dependency_overrides.clear()

# Utenti di test
@pytest.fixture
def test_user(db_session) -> User:
    """Crea un utente regolare di test."""
    user = db_session.query(User).filter(User.email == "test@example.com").first()
    if not user:
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
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
    return user

@pytest.fixture
def test_admin(db_session) -> User:
    """Crea un utente admin di test."""
    admin = db_session.query(User).filter(User.email == "admin@example.com").first()
    if not admin:
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
        db_session.add(admin)
        db_session.commit()
        db_session.refresh(admin)
    return admin

@pytest.fixture
def inactive_user(db_session) -> User:
    """Crea un utente inattivo di test."""
    user = db_session.query(User).filter(User.email == "inactive@example.com").first()
    if not user:
        user = User(
            email="inactive@example.com",
            username="inactive",
            hashed_password=get_password_hash("password123"),
            full_name="Inactive User",
            role=UserRole.VIEWER,
            is_active=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
    return user

# Token di test
@pytest.fixture
def user_token(test_user) -> str:
    """Genera un token JWT per l'utente test."""
    return create_access_token(data={"sub": str(test_user.id), "role": test_user.role.value})

@pytest.fixture
def admin_token(test_admin) -> str:
    """Genera un token JWT per l'admin test."""
    return create_access_token(data={"sub": str(test_admin.id), "role": test_admin.role.value})

@pytest.fixture
def expired_token(test_user) -> str:
    """Genera un token JWT scaduto."""
    expires = timedelta(minutes=-10)  # Scaduto 10 minuti fa
    return create_access_token(data={"sub": str(test_user.id)}, expires_delta=expires)

# Fixture per il servizio di ricerca
@pytest.fixture
def search_service():
    """
    Fornisce un'istanza del servizio di ricerca SQL per i test.
    
    Returns:
        SearchService: Un'istanza del servizio di ricerca
    """
    from src.services.search_service import SearchService
    return SearchService()

# Fixture per dati di test
@pytest.fixture
def test_patterns(db_session, test_user):
    """
    Crea pattern di test nel database.
    
    Returns:
        List[PrivacyPattern]: Lista di pattern creati
    """
    from src.models.privacy_pattern import PrivacyPattern
    
    # Controlla se i pattern di test esistono già
    if db_session.query(PrivacyPattern).count() > 0:
        return db_session.query(PrivacyPattern).all()
    
    # Pattern di test con diverse caratteristiche
    patterns_data = [
        {
            "title": "Test Pattern 1",
            "description": "Minimizing data collection",
            "context": "Collecting user data",
            "problem": "Privacy concerns with excessive data",
            "solution": "Collect minimal data",
            "consequences": "Improved user trust",
            "strategy": "Minimize",
            "mvc_component": "Model",
            "created_by_id": test_user.id
        },
        {
            "title": "Test Pattern 2",
            "description": "Hiding sensitive information",
            "context": "Displaying user data",
            "problem": "Exposure of sensitive data",
            "solution": "Hide or mask sensitive fields",
            "consequences": "Reduced risk of data leakage",
            "strategy": "Hide",
            "mvc_component": "View",
            "created_by_id": test_user.id
        },
        {
            "title": "Test Pattern 3",
            "description": "Transparent privacy policy",
            "context": "Legal requirements",
            "problem": "Users not understanding policies",
            "solution": "Clear, concise privacy statements",
            "consequences": "Legal compliance and user trust",
            "strategy": "Inform",
            "mvc_component": "View",
            "created_by_id": test_user.id
        }
    ]
    
    patterns = []
    for data in patterns_data:
        pattern = PrivacyPattern(**data)
        db_session.add(pattern)
        patterns.append(pattern)
    
    db_session.commit()
    for pattern in patterns:
        db_session.refresh(pattern)
    
    return patterns

# Fixture per test di performance
@pytest.fixture
def large_dataset(db_session, test_user):
    """
    Crea un grande set di dati per test di performance.
    Attivato solo con flag --large-dataset.
    """
    if not pytest.config.getoption("--large-dataset"):
        pytest.skip("Salta test di large dataset (usa --large-dataset per eseguirli)")
        
    from src.models.privacy_pattern import PrivacyPattern
    
    # Genera 1000 pattern per test di performance
    patterns = []
    for i in range(1000):
        pattern = PrivacyPattern(
            title=f"Performance Pattern {i}",
            description=f"Description for performance testing {i}",
            context=f"Context {i}",
            problem=f"Problem {i}",
            solution=f"Solution {i}",
            consequences=f"Consequences {i}",
            strategy=f"Strategy {i % 5}",
            mvc_component=["Model", "View", "Controller"][i % 3],
            created_by_id=test_user.id
        )
        db_session.add(pattern)
        patterns.append(pattern)
    
    db_session.commit()
    return patterns

# Helper per test
@pytest.fixture
def assert_called_with_contains():
    """
    Utility per verificare che un mock sia stato chiamato con parametri 
    che contengono determinati valori.
    """
    def _assert_called_with_contains(mock_obj, **kwargs):
        """
        Verifica che il mock sia stato chiamato con parametri che contengono i valori specificati.
        
        Args:
            mock_obj: Mock object da verificare
            **kwargs: Coppie chiave-valore da cercare nei parametri
        """
        assert mock_obj.called, "Il mock non è stato chiamato"
        
        for call_args in mock_obj.call_args_list:
            args, call_kwargs = call_args
            
            match = True
            for key, value in kwargs.items():
                if key not in call_kwargs or call_kwargs[key] != value:
                    match = False
                    break
            
            if match:
                return True
                
        values_str = ", ".join(f"{k}={v}" for k, v in kwargs.items())
        calls_str = "\n".join(str(call) for call in mock_obj.call_args_list)
        pytest.fail(f"Il mock non è stato chiamato con {values_str}.\nChiamate effettuate:\n{calls_str}")
    
    return _assert_called_with_contains

# Fixture per test parametrizzati
def pytest_generate_tests(metafunc):
    """
    Genera parametri per test parametrizzati.
    """
    # Esempio: genera combinazioni di ruoli e permessi
    if "role_permission" in metafunc.fixturenames:
        metafunc.parametrize(
            "role_permission",
            [
                (UserRole.ADMIN, "read", True),
                (UserRole.ADMIN, "write", True),
                (UserRole.ADMIN, "delete", True),
                (UserRole.EDITOR, "read", True),
                (UserRole.EDITOR, "write", True),
                (UserRole.EDITOR, "delete", True),
                (UserRole.VIEWER, "read", True),
                (UserRole.VIEWER, "write", False),
                (UserRole.VIEWER, "delete", False)
            ],
            ids=lambda x: f"{x[0].value}-{x[1]}-{x[2]}"
        )