# src/models/privacy_pattern.py
from sqlalchemy import Column, Integer, String, Text, Table, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from src.models.base import Base

# Tabelle di associazione
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
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = Column(Integer, ForeignKey('users.id'))
    # Aggiungiamo un campo per conteggiare le visualizzazioni, utilizzato in alcuni metodi
    view_count = Column(Integer, default=0)
    
    # Relazioni
    gdpr_articles = relationship("GDPRArticle", secondary=pattern_gdpr_association, back_populates="patterns")
    pbd_principles = relationship("PbDPrinciple", secondary=pattern_pbd_association, back_populates="patterns")
    iso_phases = relationship("ISOPhase", secondary=pattern_iso_association, back_populates="patterns")
    vulnerabilities = relationship("Vulnerability", secondary=pattern_vulnerability_association, back_populates="patterns")
    examples = relationship("ImplementationExample", back_populates="pattern")
    created_by = relationship("User", back_populates="created_patterns")
    
    def __repr__(self):
        return f"<PrivacyPattern(id={self.id}, title='{self.title}')>"