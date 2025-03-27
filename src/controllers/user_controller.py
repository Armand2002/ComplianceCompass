# src/controllers/user_controller.py
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status

from src.models.user_model import User, UserRole
from src.models.privacy_pattern import PrivacyPattern
from src.utils.password import get_password_hash, verify_password
from src.schemas.user import UserCreate, UserUpdate

class UserController:
    """
    Controller per la gestione degli utenti.
    
    Gestisce la logica di business per operazioni sugli utenti.
    """
    
    @staticmethod
    def get_user(db: Session, user_id: int) -> Optional[User]:
        """
        Recupera un utente specifico.
        
        Args:
            db (Session): Sessione database
            user_id (int): ID dell'utente
            
        Returns:
            Optional[User]: Utente trovato o None
        """
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """
        Recupera un utente in base all'email.
        
        Args:
            db (Session): Sessione database
            email (str): Email dell'utente
            
        Returns:
            Optional[User]: Utente trovato o None
        """
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """
        Recupera un utente in base allo username.
        
        Args:
            db (Session): Sessione database
            username (str): Username dell'utente
            
        Returns:
            Optional[User]: Utente trovato o None
        """
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_users(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        role: Optional[UserRole] = None,
        search: Optional[str] = None,
        active_only: bool = True
    ) -> Dict[str, Any]:
        """
        Recupera una lista di utenti con filtri opzionali.
        
        Args:
            db (Session): Sessione database
            skip (int): Numero di record da saltare
            limit (int): Numero massimo di record da restituire
            role (UserRole, optional): Filtra per ruolo
            search (str, optional): Filtra per username o email
            active_only (bool): Filtra solo utenti attivi
            
        Returns:
            Dict[str, Any]: Dizionario con users, total, page, size, pages
        """
        query = db.query(User)
        
        # Applica filtri
        if role:
            query = query.filter(User.role == role)
        
        if active_only:
            query = query.filter(User.is_active == True)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (User.username.ilike(search_term)) | 
                (User.email.ilike(search_term)) |
                (User.full_name.ilike(search_term))
            )
        
        # Conteggio totale per la paginazione
        total = query.count()
        
        # Applica paginazione
        users = query.order_by(User.username).offset(skip).limit(limit).all()
        
        # Calcola informazioni di paginazione
        page = skip // limit + 1
        pages = (total + limit - 1) // limit  # Ceiling division
        
        return {
            "users": users,
            "total": total,
            "page": page,
            "size": limit,
            "pages": pages
        }
    
    @staticmethod
    def create_user(db: Session, user: UserCreate) -> User:
        """
        Crea un nuovo utente.
        
        Args:
            db (Session): Sessione database
            user (UserCreate): Dati utente
            
        Returns:
            User: Utente creato
            
        Raises:
            HTTPException: Se email o username sono già in uso
        """
        # Verifica se email esiste
        if UserController.get_user_by_email(db, user.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email già registrata"
            )
        
        # Verifica se username esiste
        if UserController.get_user_by_username(db, user.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username già in uso"
            )
        
        # Crea hash della password
        hashed_password = get_password_hash(user.password)
        
        # Crea nuovo utente
        db_user = User(
            email=user.email,
            username=user.username,
            hashed_password=hashed_password,
            full_name=user.full_name,
            bio=user.bio,
            avatar_url=user.avatar_url,
            role=user.role,
            is_active=True
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
    
    @staticmethod
    def update_user(db: Session, user_id: int, user_update: UserUpdate, is_admin: bool = False) -> Optional[User]:
        """
        Aggiorna un utente esistente.
        
        Args:
            db (Session): Sessione database
            user_id (int): ID dell'utente da aggiornare
            user_update (UserUpdate): Dati da aggiornare
            is_admin (bool): Se l'operazione è eseguita da un admin
            
        Returns:
            Optional[User]: Utente aggiornato o None
            
        Raises:
            HTTPException: Se l'utente non esiste o email/username sono già in uso
        """
        db_user = db.query(User).filter(User.id == user_id).first()
        
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Utente con ID {user_id} non trovato"
            )
        
        # Verifica email unica se cambiata
        if user_update.email and user_update.email != db_user.email:
            if UserController.get_user_by_email(db, user_update.email):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email già in uso"
                )
        
        # Verifica username unico se cambiato
        if user_update.username and user_update.username != db_user.username:
            if UserController.get_user_by_username(db, user_update.username):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username già in uso"
                )
        
        # Aggiorna campi
        update_data = user_update.dict(exclude_unset=True)
        
        # Solo un admin può cambiare il ruolo e lo stato attivo
        if not is_admin:
            update_data.pop("role", None)
            update_data.pop("is_active", None)
        
        for key, value in update_data.items():
            setattr(db_user, key, value)
        
        db.commit()
        db.refresh(db_user)
        
        return db_user
    
    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """
        Elimina un utente.
        
        Args:
            db (Session): Sessione database
            user_id (int): ID dell'utente da eliminare
            
        Returns:
            bool: True se l'operazione è riuscita
            
        Raises:
            HTTPException: Se l'utente non esiste
        """
        db_user = db.query(User).filter(User.id == user_id).first()
        
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Utente con ID {user_id} non trovato"
            )
        
        db.delete(db_user)
        db.commit()
        
        return True
    
    @staticmethod
    def get_user_profile(db: Session, user_id: int) -> Dict[str, Any]:
        """
        Recupera il profilo completo di un utente.
        
        Args:
            db (Session): Sessione database
            user_id (int): ID dell'utente
            
        Returns:
            Dict[str, Any]: Profilo utente con statistiche
            
        Raises:
            HTTPException: Se l'utente non esiste
        """
        db_user = db.query(User).filter(User.id == user_id).first()
        
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Utente con ID {user_id} non trovato"
            )
        
        # Ottieni conteggio pattern creati
        patterns_count = db.query(func.count(PrivacyPattern.id)).filter(
            PrivacyPattern.created_by_id == user_id
        ).scalar()
        
        return {
            "user": db_user,
            "created_patterns_count": patterns_count
        }
    
    @staticmethod
    def change_password(
        db: Session, 
        user_id: int, 
        current_password: str, 
        new_password: str
    ) -> bool:
        """
        Cambia la password di un utente.
        
        Args:
            db (Session): Sessione database
            user_id (int): ID dell'utente
            current_password (str): Password attuale
            new_password (str): Nuova password
            
        Returns:
            bool: True se l'operazione è riuscita
            
        Raises:
            HTTPException: Se l'utente non esiste o la password attuale è errata
        """
        db_user = db.query(User).filter(User.id == user_id).first()
        
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Utente con ID {user_id} non trovato"
            )
        
        # Verifica password attuale
        if not verify_password(current_password, db_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password attuale non corretta"
            )
        
        # Aggiorna password
        db_user.hashed_password = get_password_hash(new_password)
        db.commit()
        
        return True