# src/controllers/auth_controller.py
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError

from src.models.user_model import User, UserRole
from src.utils.password import verify_password, get_password_hash
from src.utils.jwt import create_access_token, create_refresh_token, decode_token
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
        access_token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
        # Aggiorna l'ultimo accesso
        user.last_login = datetime.utcnow()
        db.commit()
    
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    
    @staticmethod
    def refresh_token(db: Session, token: str) -> dict:
        """
        Rinnova un access token utilizzando un refresh token valido.
        
        Args:
            db (Session): Sessione database
            token (str): Refresh token
            
        Returns:
            dict: Nuovo access token
            
        Raises:
            HTTPException: Se il token non è valido
        """
        try:
            # Verifica il refresh token
            payload = decode_token(token)
            user_id = payload.get("sub")
            
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token non valido",
                    headers={"WWW-Authenticate": "Bearer"},
                )
                
            # Verifica che l'utente esista ancora
            user = db.query(User).filter(User.id == user_id).first()
            if not user or not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Utente non trovato o disattivato",
                    headers={"WWW-Authenticate": "Bearer"},
                )
                
            # Genera un nuovo access token
            access_token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
            
            # Opzionalmente, genera anche un nuovo refresh token
            refresh_token = create_refresh_token(data={"sub": str(user.id)})
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer"
            }
            
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token non valido o scaduto",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
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
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return new_user
    
    @staticmethod
    def change_password(db: Session, user_id: int, current_password: str, new_password: str) -> bool:
        """
        Cambia la password di un utente.
        
        Args:
            db (Session): Sessione database
            user_id (int): ID dell'utente
            current_password (str): Password attuale
            new_password (str): Nuova password
            
        Returns:
            bool: True se cambio password riuscito
            
        Raises:
            HTTPException: Se la password attuale è errata o la nuova non soddisfa i requisiti
        """
        # Verifica che l'utente esista
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utente non trovato"
            )
        
        # Verifica la password attuale
        if not verify_password(current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password attuale non corretta"
            )
        
        # Verifica che la nuova password soddisfi i requisiti di complessità
        if len(new_password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La password deve essere di almeno 8 caratteri"
            )
        
        # Aggiorna la password dell'utente
        user.hashed_password = get_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        db.commit()
        
        return True