"""
Modelli per la gestione delle newsletter.
"""
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List

from sqlalchemy import Column, String, Boolean, DateTime, Text, JSON, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from src.models.base import Base


class NewsletterSubscriber(Base):
    """Modello per gli abbonati alla newsletter."""
    __tablename__ = "newsletter_subscribers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), nullable=False, unique=True, index=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    confirmation_token = Column(String(255), nullable=True, unique=True)
    is_confirmed = Column(Boolean, nullable=False, default=False)
    preferences = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relazioni
    deliveries = relationship("NewsletterDelivery", back_populates="subscriber", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<NewsletterSubscriber email={self.email}, active={self.is_active}, confirmed={self.is_confirmed}>"


class NewsletterCampaign(Base):
    """Modello per le campagne newsletter."""
    __tablename__ = "newsletter_campaigns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    content_html = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="draft")  # draft, scheduled, sent, cancelled
    scheduled_at = Column(DateTime, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    target_segment = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relazioni
    deliveries = relationship("NewsletterDelivery", back_populates="campaign", cascade="all, delete-orphan")
    created_by = relationship("User")

    def __repr__(self):
        return f"<NewsletterCampaign title={self.title}, status={self.status}>"


class NewsletterDelivery(Base):
    """Modello per tracciare l'invio delle newsletter."""
    __tablename__ = "newsletter_deliveries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("newsletter_campaigns.id", ondelete="CASCADE"), nullable=False)
    subscriber_id = Column(UUID(as_uuid=True), ForeignKey("newsletter_subscribers.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), nullable=False, default="pending")  # pending, sent, delivered, opened, clicked, bounced, failed
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    opened_at = Column(DateTime, nullable=True)
    clicked_at = Column(DateTime, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relazioni
    campaign = relationship("NewsletterCampaign", back_populates="deliveries")
    subscriber = relationship("NewsletterSubscriber", back_populates="deliveries")

    def __repr__(self):
        return f"<NewsletterDelivery campaign={self.campaign_id}, subscriber={self.subscriber_id}, status={self.status}>"


class NewsletterSubscription(Base):
    """Model for newsletter subscriptions."""
    __tablename__ = "newsletter_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class NewsletterIssue(Base):
    """Model for newsletter issues."""
    __tablename__ = "newsletter_issues"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by_id = Column(Integer, ForeignKey("users.id"))
    
    created_by = relationship("User", back_populates="newsletter_issues")