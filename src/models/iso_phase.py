# src/models/iso_phase.py
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from src.models.base import Base
from src.models.privacy_pattern import pattern_iso_association

class ISOPhase(Base):
    """
    Modello per le fasi ISO del ciclo di vita dello sviluppo software.
    
    Memorizza informazioni sulle fasi ISO che possono essere associate ai Privacy Pattern.
    """
    __tablename__ = "iso_phases"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    standard = Column(String(50), nullable=False)  # es. "ISO/IEC 27001", "ISO/IEC 29100"
    description = Column(Text, nullable=False)
    order = Column(Integer)  # Per ordinare le fasi in sequenza
    
    # Relazioni
    patterns = relationship("PrivacyPattern", secondary=pattern_iso_association, back_populates="iso_phases")
    
    def __repr__(self):
        return f"<ISOPhase(id={self.id}, name='{self.name}', standard='{self.standard}')>"