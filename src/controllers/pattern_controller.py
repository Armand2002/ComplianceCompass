# src/controllers/pattern_controller.py
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from fastapi import HTTPException, status

from src.models.privacy_pattern import PrivacyPattern
from src.models.gdpr_model import GDPRArticle
from src.models.pbd_principle import PbDPrinciple
from src.models.iso_phase import ISOPhase
from src.models.vulnerability import Vulnerability
from src.models.user_model import User
from src.models.implementation_example import ImplementationExample
from src.schemas.privacy_pattern import PatternCreate, PatternUpdate

class PatternController:
    """
    Controller per la gestione dei Privacy Pattern.
    
    Gestisce la logica di business per operazioni CRUD sui pattern.
    """
    
    @staticmethod
    def get_pattern(db: Session, pattern_id: int) -> Optional[PrivacyPattern]:
        """
        Recupera un pattern specifico dal database.
        
        Args:
            db (Session): Sessione database
            pattern_id (int): ID del pattern da recuperare
            
        Returns:
            Optional[PrivacyPattern]: Pattern trovato o None
        """
        return db.query(PrivacyPattern).filter(PrivacyPattern.id == pattern_id).first()
    
    @staticmethod
    def get_patterns(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        strategy: Optional[str] = None,
        mvc_component: Optional[str] = None,
        gdpr_id: Optional[int] = None,
        pbd_id: Optional[int] = None,
        iso_id: Optional[int] = None,
        vulnerability_id: Optional[int] = None,
        search_term: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Recupera una lista di pattern con filtri opzionali.
        
        Args:
            db (Session): Sessione database
            skip (int): Numero di record da saltare
            limit (int): Numero massimo di record da restituire
            strategy (str, optional): Filtra per strategia
            mvc_component (str, optional): Filtra per componente MVC
            gdpr_id (int, optional): Filtra per articolo GDPR
            pbd_id (int, optional): Filtra per principio PbD
            iso_id (int, optional): Filtra per fase ISO
            vulnerability_id (int, optional): Filtra per vulnerabilità
            search_term (str, optional): Termine di ricerca
            
        Returns:
            Dict[str, Any]: Dizionario con patterns, total, page, size, pages
        """
        query = db.query(PrivacyPattern)
        
        # Applica filtri se presenti
        if strategy:
            query = query.filter(PrivacyPattern.strategy == strategy)
        
        if mvc_component:
            query = query.filter(PrivacyPattern.mvc_component == mvc_component)
        
        if gdpr_id:
            query = query.join(PrivacyPattern.gdpr_articles).filter(GDPRArticle.id == gdpr_id)
        
        if pbd_id:
            query = query.join(PrivacyPattern.pbd_principles).filter(PbDPrinciple.id == pbd_id)
        
        if iso_id:
            query = query.join(PrivacyPattern.iso_phases).filter(ISOPhase.id == iso_id)
        
        if vulnerability_id:
            query = query.join(PrivacyPattern.vulnerabilities).filter(Vulnerability.id == vulnerability_id)
        
        if search_term:
            search = f"%{search_term}%"
            query = query.filter(
                or_(
                    PrivacyPattern.title.ilike(search),
                    PrivacyPattern.description.ilike(search),
                    PrivacyPattern.context.ilike(search),
                    PrivacyPattern.problem.ilike(search),
                    PrivacyPattern.solution.ilike(search)
                )
            )
        
        # Conteggio totale per la paginazione
        total = query.count()
        
        # Applica paginazione
        patterns = query.order_by(PrivacyPattern.title).offset(skip).limit(limit).all()
        
        # Calcola informazioni di paginazione
        page = skip // limit + 1
        pages = (total + limit - 1) // limit  # Ceiling division
        
        return {
            "patterns": patterns,
            "total": total,
            "page": page,
            "size": limit,
            "pages": pages
        }
    
    @staticmethod
    def create_pattern(db: Session, pattern: PatternCreate, current_user: User) -> PrivacyPattern:
        """
        Crea un nuovo pattern nel database.
        
        Args:
            db (Session): Sessione database
            pattern (PatternCreate): Dati del pattern da creare
            current_user (User): Utente che sta creando il pattern
            
        Returns:
            PrivacyPattern: Pattern creato
            
        Raises:
            HTTPException: Se il titolo è già in uso
        """
        # Verifica se esiste già un pattern con lo stesso titolo
        existing = db.query(PrivacyPattern).filter(PrivacyPattern.title == pattern.title).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Pattern con titolo '{pattern.title}' già esistente"
            )
        
        # Crea il nuovo pattern
        db_pattern = PrivacyPattern(
            title=pattern.title,
            description=pattern.description,
            context=pattern.context,
            problem=pattern.problem,
            solution=pattern.solution,
            consequences=pattern.consequences,
            strategy=pattern.strategy,
            mvc_component=pattern.mvc_component,
            created_by_id=current_user.id
        )
        
        # Aggiungi relazioni se presenti
        if pattern.gdpr_ids:
            gdpr_articles = db.query(GDPRArticle).filter(GDPRArticle.id.in_(pattern.gdpr_ids)).all()
            db_pattern.gdpr_articles = gdpr_articles
        
        if pattern.pbd_ids:
            pbd_principles = db.query(PbDPrinciple).filter(PbDPrinciple.id.in_(pattern.pbd_ids)).all()
            db_pattern.pbd_principles = pbd_principles
        
        if pattern.iso_ids:
            iso_phases = db.query(ISOPhase).filter(ISOPhase.id.in_(pattern.iso_ids)).all()
            db_pattern.iso_phases = iso_phases
        
        if pattern.vulnerability_ids:
            vulnerabilities = db.query(Vulnerability).filter(Vulnerability.id.in_(pattern.vulnerability_ids)).all()
            db_pattern.vulnerabilities = vulnerabilities
        
        # Salva nel database
        db.add(db_pattern)
        db.commit()
        db.refresh(db_pattern)
        
        return db_pattern
    
    @staticmethod
    def update_pattern(
        db: Session, 
        pattern_id: int, 
        pattern_update: PatternUpdate, 
        current_user: User
    ) -> Optional[PrivacyPattern]:
        """
        Aggiorna un pattern esistente.
        
        Args:
            db (Session): Sessione database
            pattern_id (int): ID del pattern da aggiornare
            pattern_update (PatternUpdate): Dati aggiornati
            current_user (User): Utente che sta effettuando l'aggiornamento
            
        Returns:
            Optional[PrivacyPattern]: Pattern aggiornato o None
            
        Raises:
            HTTPException: Se il pattern non esiste o l'utente non è autorizzato
        """
        # Recupera il pattern
        db_pattern = db.query(PrivacyPattern).filter(PrivacyPattern.id == pattern_id).first()
        
        if not db_pattern:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pattern con ID {pattern_id} non trovato"
            )
        
        # Verifica autorizzazione (solo admin o creatore)
        if not current_user.is_admin and db_pattern.created_by_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Non sei autorizzato a modificare questo pattern"
            )
        
        # Verifica unicità del titolo se aggiornato
        if pattern_update.title and pattern_update.title != db_pattern.title:
            existing = db.query(PrivacyPattern).filter(PrivacyPattern.title == pattern_update.title).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Pattern con titolo '{pattern_update.title}' già esistente"
                )
        
        # Aggiorna i campi
        update_data = pattern_update.dict(exclude_unset=True)
        
        # Gestisci le relazioni separatamente
        relation_fields = ["gdpr_ids", "pbd_ids", "iso_ids", "vulnerability_ids"]
        for field in update_data.copy():
            if field not in relation_fields:
                setattr(db_pattern, field, update_data[field])
                del update_data[field]
        
        # Aggiorna relazioni se presenti
        if "gdpr_ids" in update_data and update_data["gdpr_ids"] is not None:
            gdpr_articles = db.query(GDPRArticle).filter(GDPRArticle.id.in_(update_data["gdpr_ids"])).all()
            db_pattern.gdpr_articles = gdpr_articles
        
        if "pbd_ids" in update_data and update_data["pbd_ids"] is not None:
            pbd_principles = db.query(PbDPrinciple).filter(PbDPrinciple.id.in_(update_data["pbd_ids"])).all()
            db_pattern.pbd_principles = pbd_principles
        
        if "iso_ids" in update_data and update_data["iso_ids"] is not None:
            iso_phases = db.query(ISOPhase).filter(ISOPhase.id.in_(update_data["iso_ids"])).all()
            db_pattern.iso_phases = iso_phases
        
        if "vulnerability_ids" in update_data and update_data["vulnerability_ids"] is not None:
            vulnerabilities = db.query(Vulnerability).filter(Vulnerability.id.in_(update_data["vulnerability_ids"])).all()
            db_pattern.vulnerabilities = vulnerabilities
        
        # Salva nel database
        db.commit()
        db.refresh(db_pattern)
        
        return db_pattern
    
    @staticmethod
    def delete_pattern(db: Session, pattern_id: int, current_user: User) -> bool:
        """
        Elimina un pattern.
        
        Args:
            db (Session): Sessione database
            pattern_id (int): ID del pattern da eliminare
            current_user (User): Utente che sta effettuando l'eliminazione
            
        Returns:
            bool: True se eliminato con successo
            
        Raises:
            HTTPException: Se il pattern non esiste o l'utente non è autorizzato
        """
        # Recupera il pattern
        db_pattern = db.query(PrivacyPattern).filter(PrivacyPattern.id == pattern_id).first()
        
        if not db_pattern:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pattern con ID {pattern_id} non trovato"
            )
        
        # Verifica autorizzazione (solo admin o creatore)
        if not current_user.is_admin and db_pattern.created_by_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Non sei autorizzato a eliminare questo pattern"
            )
        
        # Elimina il pattern
        db.delete(db_pattern)
        db.commit()
        
        return True
    
    @staticmethod
    def get_pattern_stats(db: Session) -> Dict[str, Any]:
        """
        Recupera statistiche sui pattern.
        
        Args:
            db (Session): Sessione database
            
        Returns:
            Dict[str, Any]: Statistiche sui pattern
        """
        total_patterns = db.query(func.count(PrivacyPattern.id)).scalar()
        
        # Conteggio per strategia
        strategy_counts = db.query(
            PrivacyPattern.strategy, 
            func.count(PrivacyPattern.id).label("count")
        ).group_by(PrivacyPattern.strategy).all()
        
        # Conteggio per componente MVC
        mvc_counts = db.query(
            PrivacyPattern.mvc_component, 
            func.count(PrivacyPattern.id).label("count")
        ).group_by(PrivacyPattern.mvc_component).all()
        
        return {
            "total": total_patterns,
            "strategies": {s: c for s, c in strategy_counts},
            "mvc_components": {m: c for m, c in mvc_counts}
        }
    
@staticmethod
def get_patterns_by_category(db: Session, category: str) -> List[PrivacyPattern]:
    """
    Recupera pattern per categoria.
    
    Args:
        db (Session): Sessione database
        category (str): Categoria da filtrare
        
    Returns:
        List[PrivacyPattern]: Lista di pattern nella categoria
    """
    patterns = db.query(PrivacyPattern).filter(
        PrivacyPattern.strategy == category
    ).all()
    
    return patterns

@staticmethod
def get_related_patterns(db: Session, pattern: PrivacyPattern, limit: int = 5) -> List[PrivacyPattern]:
    """
    Trova pattern correlati a un pattern specifico.
    
    Args:
        db (Session): Sessione database
        pattern (PrivacyPattern): Pattern di riferimento
        limit (int): Numero massimo di pattern da restituire
        
    Returns:
        List[PrivacyPattern]: Lista di pattern correlati
    """
    # Raccogli gli ID degli articoli GDPR correlati
    gdpr_ids = [article.id for article in pattern.gdpr_articles]
    
    # Cerca pattern che condividono articoli GDPR
    query = db.query(PrivacyPattern).filter(
        PrivacyPattern.id != pattern.id  # Escludi il pattern corrente
    ).join(
        PrivacyPattern.gdpr_articles
    ).filter(
        GDPRArticle.id.in_(gdpr_ids)
    ).distinct()
    
    # Aggiungi pattern della stessa strategia
    query_strategy = db.query(PrivacyPattern).filter(
        PrivacyPattern.id != pattern.id,  # Escludi il pattern corrente
        PrivacyPattern.strategy == pattern.strategy
    )
    
    # Unisci i risultati e limita
    related_patterns = query.union(query_strategy).limit(limit).all()
    
    return related_patterns