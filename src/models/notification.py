# src/models/notification.py
import enum
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.models.base import Base

class NotificationType(enum.Enum):
    """Tipi di notifica supportati."""
    SYSTEM = "system"
    INFO = "info"
    WARNING = "warning"
    SUCCESS = "success"
    PRIVACY_PATTERN = "privacy_pattern"
    COMMENT = "comment"
    NEWSLETTER = "newsletter"

class Notification(Base):
    """Modello per le notifiche agli utenti."""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    message = Column(Text, nullable=False)
    link = Column(String(255), nullable=True)
    is_read = Column(Boolean, default=False)
    type = Column(Enum(NotificationType), default=NotificationType.INFO, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relazione con User
    user = relationship("User", back_populates="notifications")