# src/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.config import settings

# Usa l'URL del database dalle impostazioni
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Crea l'istanza del motore
connect_args = {}
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=connect_args,
    echo=settings.DEBUG
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