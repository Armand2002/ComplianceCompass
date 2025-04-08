# src/models/user_model.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from src.models.base import Base

class UserRole(enum.Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"

class User(Base):
    """
    Modello per gli utenti dell'applicazione.
    
    Memorizza informazioni sull'utente, credenziali e preferenze.
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role = Column(Enum(UserRole), default=UserRole.VIEWER)
    is_active = Column(Boolean, default=True)
    bio = Column(Text)
    avatar_url = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relazioni
    created_patterns = relationship("PrivacyPattern", back_populates="created_by")
    notifications = relationship("Notification", back_populates="user")
    newsletter_issues = relationship("NewsletterIssue", back_populates="created_by")
    
    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN
    
    @property
    def is_editor(self):
        return self.role in [UserRole.ADMIN, UserRole.EDITOR]
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role={self.role})>"