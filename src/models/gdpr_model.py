# src/models/gdpr_model.py
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from src.models.base import Base
from src.models.privacy_pattern import pattern_gdpr_association

class GDPRArticle(Base):
    """
    Modello per gli articoli del GDPR (General Data Protection Regulation).
    
    Memorizza informazioni sugli articoli GDPR rilevanti per i Privacy Pattern.
    """
    __tablename__ = "gdpr_articles"
    
    id = Column(Integer, primary_key=True, index=True)
    number = Column(String(10), unique=True, nullable=False, index=True)  # es. "5.1.a"
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text)
    category = Column(String(100), index=True)  # es. "Principi", "Diritti", ecc.
    
    # Relazioni
    patterns = relationship("PrivacyPattern", secondary=pattern_gdpr_association, back_populates="gdpr_articles")
    
    def __repr__(self):
        return f"<GDPRArticle(id={self.id}, number='{self.number}', title='{self.title}')>"