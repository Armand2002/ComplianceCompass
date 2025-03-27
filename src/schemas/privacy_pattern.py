# src/schemas/privacy_pattern.py
from typing import List, Optional, Annotated
from datetime import datetime
from pydantic import BaseModel, Field, constr

# Schemi di base
class PatternBase(BaseModel):
    """Schema base per i Privacy Pattern."""
    title: Annotated[str, constr(min_length=3, max_length=255)] = Field(..., description="Titolo del pattern")
    description: Annotated[str, constr(min_length=10)] = Field(..., description="Descrizione generale del pattern")
    context: Annotated[str, constr(min_length=10)] = Field(..., description="Contesto in cui il pattern è applicabile")
    problem: Annotated[str, constr(min_length=10)] = Field(..., description="Problema che il pattern risolve")
    solution: Annotated[str, constr(min_length=10)] = Field(..., description="Soluzione proposta dal pattern")
    consequences: Annotated[str, constr(min_length=10)] = Field(..., description="Conseguenze dell'applicazione del pattern")
    strategy: Annotated[str, constr(min_length=3, max_length=100)] = Field(..., description="Strategia di privacy (es. Minimize, Hide, Abstract)")
    mvc_component: Annotated[str, constr(min_length=3, max_length=50)] = Field(..., description="Componente MVC (Model, View, Controller)")

# Schema per la creazione
class PatternCreate(PatternBase):
    """Schema per la creazione di un nuovo Privacy Pattern."""
    gdpr_ids: List[int] = Field(default=[], description="ID degli articoli GDPR correlati")
    pbd_ids: List[int] = Field(default=[], description="ID dei principi Privacy by Design correlati")
    iso_ids: List[int] = Field(default=[], description="ID delle fasi ISO correlate")
    vulnerability_ids: List[int] = Field(default=[], description="ID delle vulnerabilità correlate")

# Schema per l'aggiornamento
class PatternUpdate(BaseModel):
    """Schema per l'aggiornamento di un Privacy Pattern esistente."""
    title: Optional[Annotated[str, constr(min_length=3, max_length=255)]] = None
    description: Optional[Annotated[str, constr(min_length=10)]] = None
    context: Optional[Annotated[str, constr(min_length=10)]] = None
    problem: Optional[Annotated[str, constr(min_length=10)]] = None
    solution: Optional[Annotated[str, constr(min_length=10)]] = None
    consequences: Optional[Annotated[str, constr(min_length=10)]] = None
    strategy: Optional[Annotated[str, constr(min_length=3, max_length=100)]] = None
    mvc_component: Optional[Annotated[str, constr(min_length=3, max_length=50)]] = None
    gdpr_ids: Optional[List[int]] = None
    pbd_ids: Optional[List[int]] = None
    iso_ids: Optional[List[int]] = None
    vulnerability_ids: Optional[List[int]] = None

# Schema per le relazioni
class GDPRArticleBase(BaseModel):
    """Schema base per gli articoli GDPR."""
    id: int
    number: str
    title: str

class PbDPrincipleBase(BaseModel):
    """Schema base per i principi Privacy by Design."""
    id: int
    name: str
    description: str

class ISOPhaseBase(BaseModel):
    """Schema base per le fasi ISO."""
    id: int
    name: str
    standard: str

class VulnerabilityBase(BaseModel):
    """Schema base per le vulnerabilità."""
    id: int
    name: str
    severity: str

class ImplementationExampleBase(BaseModel):
    """Schema base per gli esempi di implementazione."""
    id: int
    title: str
    description: str
    language: Optional[str] = None

# Schema per la risposta
class PatternResponse(PatternBase):
    """Schema per la risposta con un Privacy Pattern completo."""
    id: int
    created_at: datetime
    updated_at: datetime
    created_by_id: Optional[int] = None
    gdpr_articles: List[GDPRArticleBase] = []
    pbd_principles: List[PbDPrincipleBase] = []
    iso_phases: List[ISOPhaseBase] = []
    vulnerabilities: List[VulnerabilityBase] = []
    examples: List[ImplementationExampleBase] = []

    class Config:
        orm_mode = True

# Schema per la lista di pattern
class PatternList(BaseModel):
    """Schema per la lista di Privacy Pattern."""
    patterns: List[PatternResponse]
    total: int
    page: int
    size: int
    pages: int

# Schema per la ricerca
class PatternSearch(BaseModel):
    """Schema per la ricerca di Privacy Pattern."""
    query: Optional[str] = None
    strategy: Optional[str] = None
    mvc_component: Optional[str] = None
    gdpr_ids: Optional[List[int]] = None
    pbd_ids: Optional[List[int]] = None
    iso_ids: Optional[List[int]] = None
    vulnerability_ids: Optional[List[int]] = None
    page: int = 1
    size: int = 10