# src/routes/auth_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.controllers.auth_controller import AuthController
from src.middleware.auth_middleware import get_current_user
from src.models.user_model import User
from src.schemas.auth import UserRegister, Token, PasswordChange, PasswordReset, PasswordResetConfirm
from src.schemas.user import UserResponse

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

@router.post("/request-password-reset")
async def request_password_reset(
    reset_data: PasswordReset,
    db: Session = Depends(get_db)
):
    """
    Richiede un reset della password.
    
    Invia un'email con un link per il reset (implementazione da completare).
    """
    # Questa è una funzione placeholder
    # In una implementazione reale, genererai un token e invierai un'email
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
    # Questa è una funzione placeholder
    # In una implementazione reale, verificherai il token e cambierai la password
    if reset_data.new_password != reset_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le password non corrispondono"
        )
    
    return {"message": "Password resettata con successo"}