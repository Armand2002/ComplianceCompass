# src/models/newsletter.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from src.models.base import Base
from src.models.user_model import User

class NewsletterSubscription(Base):
    """
    Modello per le iscrizioni alla newsletter.
    
    Memorizza informazioni sugli utenti iscritti alla newsletter.
    """
    __tablename__ = "newsletter_subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True, index=True)  # Aggiunto indice
    is_verified = Column(Boolean, default=False, index=True)  # Aggiunto indice
    verification_token = Column(String(100), nullable=True)
    subscribed_at = Column(DateTime, default=datetime.utcnow)
    last_updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Associazione facoltativa con l'utente (se registrato)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    user = relationship("User", backref="newsletter_subscription")
    
    # Aggiungiamo un indice composto per le query più frequenti
    __table_args__ = (
        Index('idx_active_verified', 'is_active', 'is_verified'),
    )
    
    def __repr__(self):
        return f"<NewsletterSubscription(id={self.id}, email='{self.email}', is_verified={self.is_verified})>"


class NewsletterIssue(Base):
    """
    Modello per le edizioni della newsletter.
    
    Memorizza informazioni sulle newsletter inviate.
    """
    __tablename__ = "newsletter_issues"
    
    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by_id = Column(Integer, ForeignKey('users.id'))
    
    # Relazioni
    created_by = relationship("User")
    
    def __repr__(self):
        return f"<NewsletterIssue(id={self.id}, subject='{self.subject}')>"