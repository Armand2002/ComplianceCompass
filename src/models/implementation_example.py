# src/models/implementation_example.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from src.models.base import Base

class ImplementationExample(Base):
    """
    Modello per gli esempi di implementazione dei Privacy Pattern.
    
    Memorizza codice, diagrammi o altri esempi pratici di come implementare un pattern.
    """
    __tablename__ = "implementation_examples"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    code = Column(Text)
    language = Column(String(50))  # es. "Python", "Java", "JavaScript"
    diagram_url = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = Column(Integer, ForeignKey('users.id'))
    pattern_id = Column(Integer, ForeignKey('privacy_patterns.id'), nullable=False)
    
    # Relazioni
    pattern = relationship("PrivacyPattern", back_populates="examples")
    created_by = relationship("User")
    
    def __repr__(self):
        return f"<ImplementationExample(id={self.id}, title='{self.title}', pattern_id={self.pattern_id})>"