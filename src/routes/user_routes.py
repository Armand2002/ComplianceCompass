# src/routes/user_routes.py
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.controllers.user_controller import UserController
from src.models.user_model import User, UserRole
from src.middleware.auth_middleware import get_current_user, get_current_admin_user
from src.schemas.user import UserResponse, UserList, UserCreate, UserUpdate, UserProfile
from src.schemas.auth import PasswordChange

# Crea il router
router = APIRouter(
    prefix="/users",
    tags=["utenti"],
    responses={401: {"description": "Non autorizzato"}}
)

@router.get("/", response_model=UserList)
async def get_users(
    skip: int = Query(0, ge=0, description="Numero di record da saltare"),
    limit: int = Query(10, ge=1, le=100, description="Numero massimo di record da restituire"),
    role: Optional[UserRole] = Query(None, description="Filtra per ruolo"),
    search: Optional[str] = Query(None, description="Cerca per username, email o nome"),
    active_only: bool = Query(True, description="Filtra solo utenti attivi"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Recupera un elenco di utenti.
    
    Richiede privilegi di amministratore.
    """
    result = UserController.get_users(
        db=db,
        skip=skip,
        limit=limit,
        role=role,
        search=search,
        active_only=active_only
    )
    
    return UserList(
        users=result["users"],
        total=result["total"],
        page=result["page"],
        size=limit,
        pages=result["pages"]
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Recupera informazioni sull'utente corrente.
    """
    return current_user

@router.get("/profile", response_model=UserProfile)
async def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Recupera il profilo completo dell'utente corrente.
    """
    result = UserController.get_user_profile(db=db, user_id=current_user.id)
    
    profile = UserProfile(
        **{k: getattr(result["user"], k) for k in UserResponse.__annotations__.keys()},
        created_patterns_count=result["created_patterns_count"]
    )
    
    return profile

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Recupera un utente specifico.
    
    Richiede privilegi di amministratore.
    """
    user = UserController.get_user(db=db, user_id=user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Utente con ID {user_id} non trovato"
        )
    
    return user

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Crea un nuovo utente.
    
    Richiede privilegi di amministratore.
    """
    return UserController.create_user(db=db, user=user)

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Aggiorna informazioni dell'utente corrente.
    """
    return UserController.update_user(
        db=db,
        user_id=current_user.id,
        user_update=user_update,
        is_admin=current_user.is_admin
    )

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Aggiorna informazioni di un utente specifico.
    
    Richiede privilegi di amministratore.
    """
    return UserController.update_user(
        db=db,
        user_id=user_id,
        user_update=user_update,
        is_admin=True
    )

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Elimina un utente.
    
    Richiede privilegi di amministratore. Non è possibile eliminare se stessi.
    """
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Non puoi eliminare il tuo account"
        )
    
    UserController.delete_user(db=db, user_id=user_id)
    
    return {"message": "Utente eliminato con successo"}

@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cambia la password dell'utente corrente.
    """
    if password_data.new_password != password_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le password non corrispondono"
        )
    
    UserController.change_password(
        db=db,
        user_id=current_user.id,
        current_password=password_data.current_password,
        new_password=password_data.new_password
    )
    
    return {"message": "Password cambiata con successo"}