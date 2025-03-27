# src/db/session.py
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Carica variabili d'ambiente
load_dotenv()

# Determina l'URL del database in base all'ambiente
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == "production":
    SQLALCHEMY_DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@db:5432/compliance_compass"
    )
else:
    # Usa SQLite per lo sviluppo locale
    SQLALCHEMY_DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "sqlite:///./compliance_compass.db"
    )
    # SQLite richiede il connect_args per supportare il multi-threading
    connect_args = {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}

# Crea l'istanza del motore
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=connect_args if ENVIRONMENT != "production" else {},
    echo=ENVIRONMENT != "production"  # Mostra le query SQL solo in sviluppo
)

# Sessione per interagire con il database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Funzione per ottenere una sessione DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()