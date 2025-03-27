# src/models/notification.py
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from src.models.base import Base

class NotificationType(enum.Enum):
    """Tipi di notifica supportati dal sistema."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    UPDATE = "update"

class Notification(Base):
    """
    Modello per le notifiche utente.
    
    Memorizza informazioni sulle notifiche inviate agli utenti.
    """
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(Enum(NotificationType), default=NotificationType.INFO)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime, nullable=True)
    related_object_id = Column(Integer, nullable=True)
    related_object_type = Column(String(50), nullable=True)
    
    # Relazioni
    user = relationship("User", back_populates="notifications")
    
    def __repr__(self):
        return f"<Notification(id={self.id}, user_id={self.user_id}, title='{self.title[:20]}...', is_read={self.is_read})>"