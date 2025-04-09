# src/models/privacy_pattern.py
from sqlalchemy import Column, Integer, String, Text, Table, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from src.models.base import Base

# Tabelle di associazione (unchanged)
pattern_gdpr_association = Table(
    'pattern_gdpr_association',
    Base.metadata,
    Column('pattern_id', Integer, ForeignKey('privacy_patterns.id')),
    Column('gdpr_id', Integer, ForeignKey('gdpr_articles.id'))
)

pattern_pbd_association = Table(
    'pattern_pbd_association',
    Base.metadata,
    Column('pattern_id', Integer, ForeignKey('privacy_patterns.id')),
    Column('pbd_id', Integer, ForeignKey('pbd_principles.id'))
)

pattern_iso_association = Table(
    'pattern_iso_association',
    Base.metadata,
    Column('pattern_id', Integer, ForeignKey('privacy_patterns.id')),
    Column('iso_id', Integer, ForeignKey('iso_phases.id'))
)

pattern_vulnerability_association = Table(
    'pattern_vulnerability_association',
    Base.metadata,
    Column('pattern_id', Integer, ForeignKey('privacy_patterns.id')),
    Column('vulnerability_id', Integer, ForeignKey('vulnerabilities.id'))
)

class PrivacyPattern(Base):
    """
    Modello per i Privacy Patterns.
    
    Un Privacy Pattern rappresenta una soluzione riutilizzabile per problemi comuni di privacy
    nella progettazione di sistemi software e informatici.
    """
    __tablename__ = "privacy_patterns"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True, unique=True)
    description = Column(Text, nullable=False)
    context = Column(Text, nullable=False)
    problem = Column(Text, nullable=False)
    solution = Column(Text, nullable=False)
    consequences = Column(Text, nullable=False)
    strategy = Column(String(100), nullable=False, index=True)
    mvc_component = Column(String(50), nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    created_by_id = Column(Integer, ForeignKey('users.id'))
    # Campo per conteggiare le visualizzazioni
    view_count = Column(Integer, nullable=True, default=0)
    
    # Relazioni ottimizzate
    gdpr_articles = relationship(
        "GDPRArticle", 
        secondary=pattern_gdpr_association, 
        back_populates="patterns",
        lazy="selectin"  # Strategia di caricamento ottimizzata
    )
    
    pbd_principles = relationship(
        "PbDPrinciple", 
        secondary=pattern_pbd_association, 
        back_populates="patterns",
        lazy="selectin"
    )
    
    iso_phases = relationship(
        "ISOPhase", 
        secondary=pattern_iso_association, 
        back_populates="patterns",
        lazy="selectin"
    )
    
    vulnerabilities = relationship(
        "Vulnerability", 
        secondary=pattern_vulnerability_association, 
        back_populates="patterns",
        lazy="selectin"
    )
    
    examples = relationship("ImplementationExample", back_populates="pattern")
    created_by = relationship("User", back_populates="created_patterns")
    
    def __repr__(self):
        return f"<PrivacyPattern(id={self.id}, title='{self.title}')>"
    
    def to_dict(self):
        """Converte l'oggetto in un dizionario in modo sicuro."""
        result = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "context": self.context,
            "problem": self.problem,
            "solution": self.solution,
            "consequences": self.consequences,
            "strategy": self.strategy,
            "mvc_component": self.mvc_component,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by_id": getattr(self, "created_by_id", None),
            "view_count": getattr(self, "view_count", 0),
        }
        
        # Aggiunta sicura delle relazioni solo se caricate
        if 'gdpr_articles' in self.__dict__ and self.gdpr_articles:
            result["gdpr_articles"] = [
                {"id": g.id, "number": g.number, "title": g.title} 
                for g in self.gdpr_articles
            ]
        else:
            result["gdpr_articles"] = []
            
        if 'pbd_principles' in self.__dict__ and self.pbd_principles:
            result["pbd_principles"] = [
                {"id": p.id, "name": p.name} 
                for p in self.pbd_principles
            ]
        else:
            result["pbd_principles"] = []
            
        if 'iso_phases' in self.__dict__ and self.iso_phases:
            result["iso_phases"] = [
                {"id": i.id, "name": i.name} 
                for i in self.iso_phases
            ]
        else:
            result["iso_phases"] = []
            
        if 'vulnerabilities' in self.__dict__ and self.vulnerabilities:
            result["vulnerabilities"] = [
                {"id": v.id, "cwe_id": v.cwe_id, "name": v.name} 
                for v in self.vulnerabilities
            ]
        else:
            result["vulnerabilities"] = []
        
        return result