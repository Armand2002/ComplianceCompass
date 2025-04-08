from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.models.gdpr_model import GDPRArticle

class GDPRController:
    """
    Controller per la gestione degli articoli GDPR.
    
    Gestisce la logica di business per operazioni sugli articoli GDPR.
    """
    
    @staticmethod
    def get_articles(db: Session, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Recupera una lista paginata di articoli GDPR.
        
        Args:
            db (Session): Sessione database
            skip (int): Numero di record da saltare
            limit (int): Numero massimo di record da restituire
            
        Returns:
            List[Dict[str, Any]]: Lista di articoli GDPR sotto forma di dizionari
        """
        articles = db.query(GDPRArticle).order_by(GDPRArticle.number).offset(skip).limit(limit).all()
        return [article.to_dict() for article in articles]

    @staticmethod
    def get_article(db: Session, article_id: int) -> Optional[Dict[str, Any]]:
        """
        Recupera un articolo GDPR specifico tramite ID.
        
        Args:
            db (Session): Sessione database
            article_id (int): ID dell'articolo da recuperare
            
        Returns:
            Optional[Dict[str, Any]]: Articolo come dizionario o None se non trovato
        """
        article = db.query(GDPRArticle).filter(GDPRArticle.id == article_id).first()
        if article:
            return article.to_dict()
        return None
    
    @staticmethod
    def get_article_by_number(db: Session, article_number: str) -> Optional[Dict[str, Any]]:
        """
        Recupera un articolo GDPR specifico tramite numero.
        
        Args:
            db (Session): Sessione database
            article_number (str): Numero dell'articolo (es. "5.1.a")
            
        Returns:
            Optional[Dict[str, Any]]: Articolo come dizionario o None se non trovato
        """
        article = db.query(GDPRArticle).filter(GDPRArticle.number == article_number).first()
        if article:
            return article.to_dict()
        return None
    
    @staticmethod
    def get_articles_by_category(db: Session, category: str, skip: int = 0, limit: int = 100) -> Dict[str, Any]:
        """
        Recupera articoli GDPR filtrati per categoria.
        
        Args:
            db (Session): Sessione database
            category (str): Categoria degli articoli
            skip (int): Numero di record da saltare
            limit (int): Numero massimo di record da restituire
            
        Returns:
            Dict[str, Any]: Dizionario con articoli e metadati
        """
        query = db.query(GDPRArticle).filter(GDPRArticle.category == category)
        total = query.count()
        
        articles = query.order_by(GDPRArticle.number).offset(skip).limit(limit).all()
        
        return {
            "items": [article.to_dict() for article in articles],
            "total": total,
            "page": skip // limit + 1 if limit > 0 else 1,
            "pages": (total + limit - 1) // limit if limit > 0 else 1
        }
    
    @staticmethod
    def search_articles(db: Session, query: str, skip: int = 0, limit: int = 100) -> Dict[str, Any]:
        """
        Cerca articoli GDPR in base a una query testuale.
        
        Args:
            db (Session): Sessione database
            query (str): Termine di ricerca
            skip (int): Numero di record da saltare
            limit (int): Numero massimo di record da restituire
            
        Returns:
            Dict[str, Any]: Dizionario con articoli trovati e metadati
        """
        search = f"%{query}%"
        search_query = db.query(GDPRArticle).filter(
            (GDPRArticle.title.ilike(search)) |
            (GDPRArticle.content.ilike(search)) |
            (GDPRArticle.summary.ilike(search)) |
            (GDPRArticle.number.ilike(search))
        )
        
        total = search_query.count()
        
        articles = search_query.order_by(GDPRArticle.number).offset(skip).limit(limit).all()
        
        return {
            "items": [article.to_dict() for article in articles],
            "total": total,
            "query": query,
            "page": skip // limit + 1 if limit > 0 else 1,
            "pages": (total + limit - 1) // limit if limit > 0 else 1
        }
    
    @staticmethod
    def get_gdpr_stats(db: Session) -> Dict[str, Any]:
        """
        Recupera statistiche sugli articoli GDPR.
        
        Args:
            db (Session): Sessione database
            
        Returns:
            Dict[str, Any]: Statistiche sugli articoli GDPR
        """
        total = db.query(func.count(GDPRArticle.id)).scalar()
        
        # Conteggio per categoria
        category_counts = db.query(
            GDPRArticle.category, 
            func.count(GDPRArticle.id).label("count")
        ).group_by(GDPRArticle.category).all()
        
        # Conteggio per capitolo
        chapter_counts = db.query(
            GDPRArticle.chapter, 
            func.count(GDPRArticle.id).label("count")
        ).group_by(GDPRArticle.chapter).all()
        
        # Articoli principali
        key_articles = db.query(GDPRArticle).filter(GDPRArticle.is_key_article == True).all()
        
        return {
            "total": total,
            "categories": {c: count for c, count in category_counts if c},
            "chapters": {c: count for c, count in chapter_counts if c},
            "key_articles": [article.to_dict() for article in key_articles]
        }