# src/models/gdpr_model.py
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from typing import List
from datetime import datetime, timezone
from src.models.base import Base
from src.models.privacy_pattern import pattern_gdpr_association

class GDPRArticle(Base):
    """
    Modello per gli articoli del GDPR (General Data Protection Regulation).
    
    Memorizza informazioni sugli articoli GDPR rilevanti per i Privacy Pattern.
    Ogni articolo può essere associato a molteplici pattern di privacy.
    """
    __tablename__ = "gdpr_articles"
    
    id = Column(Integer, primary_key=True, index=True)
    number = Column(String(10), unique=True, nullable=False, index=True)  # Expected format: "5.1.a" (e.g., Chapter 5, Section 1, Clause a). Valid examples: "1.2.b", "10.3.c". Invalid examples: "5.1", "abc", "5..a".
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text)
    category = Column(String(100), index=True)  # Categorie degli articoli GDPR, ad esempio "Principi" (principles) o "Diritti" (rights) definiti nel regolamento.
    chapter = Column(String(100), index=True)  # es. "Capitolo II", "Capitolo III"
    is_key_article = Column(Boolean, default=False, index=True)  # Indicates whether the article is particularly important. Key articles are those that have significant implications for compliance or are frequently referenced in privacy patterns.
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relazioni ottimizzate
    patterns = relationship(
        "PrivacyPattern", 
        secondary=pattern_gdpr_association, 
        back_populates="gdpr_articles", 
        lazy="selectin"  # Cambiato da "noload" a "selectin" per ottimizzare le query
    )
    
    def __repr__(self):
        return f"<GDPRArticle(id={self.id}, number='{self.number}', title='{self.title}')>"
    
    @property
    def pattern_count(self) -> int:
        """
        Restituisce il numero di pattern associati a questo articolo.
        
        Returns:
            int: Numero di pattern associati
        """
        return len(self.patterns) if self.patterns else 0
    
    @classmethod
    def get_by_number(cls, db_session, number: str):
        """
        Recupera un articolo GDPR basato sul suo numero.
        
        Args:
            db_session: Sessione del database
            number: Numero dell'articolo (es. "5.1.a")
            
        Returns:
            GDPRArticle o None se non trovato
        """
        if not number or not isinstance(number, str):
            return None
        return db_session.query(cls).filter(cls.number == number).first()
    
    @classmethod
    def get_by_category(cls, db_session, category: str, limit: int = None, offset: int = None) -> List["GDPRArticle"]:
        """
        Recupera gli articoli GDPR appartenenti a una specifica categoria con supporto per la paginazione.
        
        Args:
            db_session: Sessione del database
            category: Categoria degli articoli (es. "Principi")
            limit: Numero massimo di risultati da restituire
            offset: Numero di articoli da saltare
            
        Returns:
            Lista di articoli GDPR
        """
        query = db_session.query(cls).filter(cls.category == category)
        if limit is not None:
            query = query.limit(limit)
        if offset is not None:
            query = query.offset(offset)
        return query.all()
    
    def to_dict(self):
        """Converte l'oggetto in un dizionario in modo sicuro."""
        result = {
            "id": self.id,
            "number": self.number,
            "title": self.title,
            "content": self.content,
            "summary": self.summary,
            "category": self.category,
            "chapter": self.chapter,
            "is_key_article": self.is_key_article,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        
        # Aggiungi relazioni solo se caricate (evita eccezioni)
        if 'patterns' in self.__dict__:
            result["patterns"] = [
                {"id": p.id, "title": p.title} for p in self.patterns
            ]
            
        return result