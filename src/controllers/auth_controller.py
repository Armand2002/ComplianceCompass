# src/controllers/auth_controller.py
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.models.user_model import User, UserRole
from src.utils.password import verify_password, get_password_hash
from src.utils.jwt import create_access_token, create_refresh_token
from src.schemas.auth import UserRegister

class AuthController:
    """
    Controller per la gestione dell'autenticazione.
    
    Gestisce login, registrazione e token JWT.
    """
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """
        Autentica un utente verificando email e password.
        
        Args:
            db (Session): Sessione database
            email (str): Email dell'utente
            password (str): Password in chiaro
            
        Returns:
            Optional[User]: Utente autenticato o None
        """
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        return user
    
    @staticmethod
    def login(db: Session, form_data: OAuth2PasswordRequestForm) -> dict:
        """
        Gestisce il login utente e genera un token JWT.
        
        Args:
            db (Session): Sessione database
            form_data (OAuth2PasswordRequestForm): Dati di login
            
        Returns:
            dict: Token di accesso
            
        Raises:
            HTTPException: Se le credenziali sono errate
        """
        user = AuthController.authenticate_user(
            db=db, 
            email=form_data.username,  # OAuth2 usa username, ma noi usiamo email
            password=form_data.password
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email o password non corrette",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account disattivato"
            )
        
        # Genera token JWT
        access_token = create_access_token(
            data={"sub": user.id}
        )
        
        # Aggiorna l'ultimo accesso
        user.last_login = datetime.utcnow()
        db.commit()
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    
    @staticmethod
    def register(db: Session, user_data: UserRegister) -> User:
        """
        Registra un nuovo utente.
        
        Args:
            db (Session): Sessione database
            user_data (UserRegister): Dati di registrazione
            
        Returns:
            User: Utente registrato
            
        Raises:
            HTTPException: Se email o username sono già in uso
        """
        # Verifica se email già esiste
        if db.query(User).filter(User.email == user_data.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email già registrata"
            )
        
        # Verifica se username già esiste
        if db.query(User).filter(User.username == user_data.username).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username già in uso"
            )
        
        # Crea nuovo utente
        hashed_password = get_password_hash(user_data.password)
        
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            role=UserRole.VIEWER,  # Ruolo predefinito per nuovi utenti
            is_active=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return new_user
    
    @staticmethod
    def change_password(db: Session, user: User, current_password: str, new_password: str) -> bool:
        """
        Cambia la password di un utente.
        
        Args:
            db (Session): Sessione database
            user (User): Utente
            current_password (str): Password attuale
            new_password (str): Nuova password
            
        Returns:
            bool: True se cambio password riuscito
            
        Raises:
            HTTPException: Se la password attuale è errata
        """
        if not verify_password(current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password attuale non corretta"
            )
        
        # Imposta nuova password
        user.hashed_password = get_password_hash(new_password)
        db.commit()
        
        return True
    
    # Modifiche a src/controllers/auth_controller.py

    @staticmethod
    def login(db: Session, form_data: OAuth2PasswordRequestForm) -> dict:
        """
        Gestisce il login utente e genera token JWT.
    
        Args:
            db (Session): Sessione database
            form_data (OAuth2PasswordRequestForm): Dati di login
        
        Returns:
            dict: Token di accesso e refresh token
        
        Raises:
            HTTPException: Se le credenziali sono errate
        """
        user = AuthController.authenticate_user(
            db=db, 
            email=form_data.username,  # OAuth2 usa username, ma noi usiamo email
            password=form_data.password
        )
    
        if not user:
            raise HTTPException(
              status_code=status.HTTP_401_UNAUTHORIZED,
              detail="Email o password non corrette",
              headers={"WWW-Authenticate": "Bearer"},
            )
    
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account disattivato"
            )
    
        # Genera token JWT
        access_token = create_access_token(data={"sub": user.id})
        refresh_token = create_refresh_token(data={"sub": user.id})
    
        # Aggiorna l'ultimo accesso
        user.last_login = datetime.utcnow()
        db.commit()
    
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }