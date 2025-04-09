"""Controller base con implementazione standard delle operazioni CRUD."""
from typing import List, Dict, Any, TypeVar, Generic, Type, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

# Configurazione del logger
logger = logging.getLogger(__name__)

T = TypeVar('T')

class BaseController(Generic[T]):
    """
    Controller base con implementazione standard delle operazioni CRUD
    e gestione centralizzata degli errori.
    """
    
    model_class: Type[T] = None
    
    @classmethod
    def get_all(cls, db: Session, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Recupera una lista paginata di record con gestione degli errori.
        
        Args:
            db: Sessione database
            skip: Numero di record da saltare
            limit: Numero massimo di record da restituire
            
        Returns:
            Lista di record come dizionari
        """
        try:
            items = db.query(cls.model_class).offset(skip).limit(limit).all()
            return [item.to_dict() for item in items]
        except SQLAlchemyError as e:
            logger.error(f"Database error in {cls.__name__}.get_all: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in {cls.__name__}.get_all: {str(e)}")
            return []
            
    @classmethod
    def get_by_id(cls, db: Session, item_id: int) -> Optional[Dict[str, Any]]:
        """
        Recupera un record per ID con gestione degli errori.
        
        Args:
            db: Sessione database
            item_id: ID del record da recuperare
            
        Returns:
            Record come dizionario o None se non trovato
        """
        try:
            item = db.query(cls.model_class).filter(cls.model_class.id == item_id).first()
            return item.to_dict() if item else None
        except SQLAlchemyError as e:
            logger.error(f"Database error in {cls.__name__}.get_by_id({item_id}): {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in {cls.__name__}.get_by_id({item_id}): {str(e)}")
            return None

    @classmethod
    def count(cls, db: Session) -> int:
        """
        Conta il numero totale di record.
        
        Args:
            db: Sessione database
            
        Returns:
            Numero di record
        """
        try:
            return db.query(cls.model_class).count()
        except Exception as e:
            logger.error(f"Error in {cls.__name__}.count: {str(e)}")
            return 0