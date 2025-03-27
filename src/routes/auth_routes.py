# src/routes/auth_routes.py
import datetime
from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.utils.jwt import create_access_token, verify_token
from src.utils.password import get_password_hash
from src.db.session import get_db
from src.controllers.auth_controller import AuthController
from src.middleware.auth_middleware import get_current_user
from src.models.user_model import User
from src.schemas.auth import UserRegister, Token, PasswordChange, PasswordReset, PasswordResetConfirm
from src.schemas.user import UserResponse
from src.utils.email import send_password_reset_email
from src.utils.token import generate_verification_token, verify_verification_token
# Crea il router
router = APIRouter(
    prefix="/auth",
    tags=["autenticazione"],
    responses={401: {"description": "Non autorizzato"}}
)

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Autentica un utente e restituisce un token JWT.
    
    Richiede email (come username nel form) e password.
    """
    return AuthController.login(db=db, form_data=form_data)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """
    Registra un nuovo utente.
    
    Richiede email, username e password. Restituisce i dati utente (esclude password).
    """
    return AuthController.register(db=db, user_data=user_data)

@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cambia la password dell'utente corrente.
    
    Richiede la password attuale e la nuova password.
    """
    if password_data.new_password != password_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le password non corrispondono"
        )
    
    AuthController.change_password(
        db=db,
        user=current_user,
        current_password=password_data.current_password,
        new_password=password_data.new_password
    )
    
    return {"message": "Password cambiata con successo"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Restituisce informazioni sull'utente corrente.
    
    Utilizzato per verificare lo stato dell'autenticazione e ottenere i dati dell'utente.
    """
    return current_user

@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    """
    Ottiene un nuovo access token usando un refresh token.
    """
    token_data = verify_token(refresh_token)
    
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token non valido o scaduto",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = token_data.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utente non trovato o disattivato",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Genera nuovo access token
    access_token = create_access_token(data={"sub": user.id})
    
    # Aggiorna l'ultimo accesso
    user.last_login = datetime.utcnow()
    db.commit()
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/request-password-reset")
async def request_password_reset(
    email_data: PasswordReset,
    db: Session = Depends(get_db)
):
    """
    Richiede un reset della password.
    
    Invia un'email con un link per il reset.
    """
    user = db.query(User).filter(User.email == email_data.email).first()
    
    if user:
        # Genera token di verifica valido per 24 ore
        token = generate_verification_token(user.id, expiration_hours=24)
        
        # Invia email con token
        send_password_reset_email(user.email, user.username, token)
    
    # Nota: rispondiamo sempre positivamente per evitare enumeration di email
    return {"message": "Se l'email esiste, riceverai un link per il reset della password"}

@router.post("/reset-password")
async def reset_password(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """
    Resetta la password con un token.
    
    Richiede il token ricevuto via email e la nuova password.
    """
    if reset_data.new_password != reset_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le password non corrispondono"
        )
    
    # Verifica token
    user_id = verify_verification_token(reset_data.token)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token non valido o scaduto"
        )
    
    # Trova l'utente
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utente non trovato"
        )
    
    # Aggiorna password
    user.hashed_password = get_password_hash(reset_data.new_password)
    db.commit()
    
    return {"message": "Password resettata con successo"}