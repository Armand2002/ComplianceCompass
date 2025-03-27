# src/routes/notification_routes.py
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.controllers.notification_controller import NotificationController
from src.models.user_model import User
from src.middleware.auth_middleware import get_current_user
from src.schemas.notification import NotificationList, NotificationCreate, NotificationResponse
from src.models.notification import NotificationType

# Crea il router
router = APIRouter(
    prefix="/notifications",
    tags=["notifiche"],
    responses={401: {"description": "Non autorizzato"}}
)

# Istanzia il controller
notification_controller = NotificationController()

@router.get("/", response_model=NotificationList)
async def get_notifications(
    skip: int = Query(0, ge=0, description="Numero di record da saltare"),
    limit: int = Query(10, ge=1, le=100, description="Numero massimo di record da restituire"),
    unread_only: bool = Query(False, description="Filtra solo notifiche non lette"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Recupera le notifiche dell'utente corrente.
    
    Restituisce una lista paginata di notifiche.
    """
    result = notification_controller.get_user_notifications(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        unread_only=unread_only
    )
    
    return NotificationList(
        notifications=result["notifications"],
        total=result["total"],
        unread_count=result["unread_count"]
    )

@router.post("/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Marca una notifica come letta.
    
    Richiede che la notifica appartenga all'utente corrente.
    """
    notification_controller.mark_notification_read(
        db=db,
        notification_id=notification_id,
        current_user=current_user
    )
    
    return {"message": "Notifica marcata come letta con successo"}

@router.post("/read-all")
async def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Marca tutte le notifiche dell'utente come lette.
    """
    count = notification_controller.mark_all_notifications_read(
        db=db,
        current_user=current_user
    )
    
    return {"message": f"{count} notifiche marcate come lette con successo"}

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Elimina una notifica.
    
    Richiede che la notifica appartenga all'utente corrente.
    """
    notification_controller.delete_notification(
        db=db,
        notification_id=notification_id,
        current_user=current_user
    )
    
    return {"message": "Notifica eliminata con successo"}

@router.post("/", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(
    notification: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crea una nuova notifica.
    
    Solo gli amministratori possono creare notifiche per altri utenti.
    """
    # Se non sei un admin, puoi creare notifiche solo per te stesso
    if not current_user.is_admin and notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Non sei autorizzato a creare notifiche per altri utenti"
        )
    
    result = notification_controller.create_notification(
        db=db,
        user_id=notification.user_id,
        title=notification.title,
        message=notification.message,
        notification_type=notification.type,
        related_object_id=notification.related_object_id,
        related_object_type=notification.related_object_type,
        send_email=notification.send_email
    )
    
    return result