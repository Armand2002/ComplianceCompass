# src/models/pbd_principle.py
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from src.models.base import Base
from src.models.privacy_pattern import pattern_pbd_association

class PbDPrinciple(Base):
    """
    Modello per i principi Privacy by Design (PbD).
    
    Memorizza informazioni sui principi PbD che possono essere associati ai Privacy Pattern.
    """
    __tablename__ = "pbd_principles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=False)
    guidance = Column(Text)
    
    # Relazioni
    patterns = relationship("PrivacyPattern", secondary=pattern_pbd_association, back_populates="pbd_principles")
    
    def __repr__(self):
        return f"<PbDPrinciple(id={self.id}, name='{self.name}')>"
    
    def to_dict(self):
        """Converte l'oggetto in un dizionario."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }