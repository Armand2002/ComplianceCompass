# src/db/init_db.py
import logging
from sqlalchemy.orm import Session
from src.models.base import Base
from src.models.user_model import User, UserRole
from src.db.session import engine, SessionLocal
from src.utils.password import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Dati iniziali per l'admin
ADMIN_EMAIL = "admin@compliancecompass.com"
ADMIN_PASSWORD = "admin123"  # In produzione, usa una password sicura e variabili d'ambiente
ADMIN_USERNAME = "admin"

def init_db() -> None:
    # Crea tabelle
    logger.info("Creazione tabelle nel database...")
    Base.metadata.create_all(bind=engine)
    logger.info("Tabelle create con successo!")
    
    # Crea una sessione
    db = SessionLocal()
    
    # Verifica se esiste già un utente admin
    create_first_admin(db)
    
    # Chiudi la sessione
    db.close()

def create_first_admin(db: Session) -> None:
    admin = db.query(User).filter(User.email == ADMIN_EMAIL).first()
    
    if not admin:
        logger.info(f"Creazione utente admin ({ADMIN_EMAIL})...")
        admin = User(
            email=ADMIN_EMAIL,
            username=ADMIN_USERNAME,
            hashed_password=get_password_hash(ADMIN_PASSWORD),
            full_name="Administrator",
            role=UserRole.ADMIN,
            is_active=True
        )
        db.add(admin)
        db.commit()
        logger.info("Utente admin creato con successo!")
    else:
        logger.info("L'utente admin esiste già.")

if __name__ == "__main__":
    logger.info("Inizializzazione del database")
    init_db()
    logger.info("Database inizializzato con successo!")