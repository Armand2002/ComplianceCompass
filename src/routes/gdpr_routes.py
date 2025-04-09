"""API routes per gli articoli GDPR."""
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
import traceback
import logging

from src.db.session import get_db
from src.controllers.gdpr_controller import GDPRController
from src.utils.response_formatter import format_response

# Configura il logger
logger = logging.getLogger(__name__)

router = APIRouter(tags=["gdpr"])

@router.get(
    "/gdpr/test", 
    summary="Test API",
    response_description="Test semplice dell'API"
)
def test_endpoint():
    """Endpoint di test che non richiede accesso al database"""
    return format_response(data={"status": "ok", "message": "API funzionante"})

@router.get(
    "/gdpr/db-test", 
    summary="Test connessione DB",
    response_description="Test della connessione al database"
)
def test_db_connection(db: Session = Depends(get_db)):
    """Verifica la connessione al database"""
    try:
        result = db.execute(text("SELECT 1")).scalar()
        return format_response(data={"status": "ok", "db_connection": True, "result": result})
    except Exception as e:
        logger.error(f"Errore connessione DB: {str(e)}")
        return format_response(
            error=str(e),
            message="Errore connessione DB",
            traceback=traceback.format_exc()
        )

@router.get(
    "/gdpr/articles",
    summary="Lista articoli GDPR", 
    response_description="Lista paginata di articoli GDPR"
)
def get_gdpr_articles(
    response: Response,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Recupera una lista paginata di articoli GDPR con risposta standardizzata."""
    try:
        result = GDPRController.get_articles(db, skip=skip, limit=limit)
        
        # Formatta la risposta in modo standard
        return format_response(
            data={
                "items": result,
                "total": len(result),
                "page": skip // limit + 1 if limit > 0 else 1,
                "pages": (len(result) + limit - 1) // limit if limit > 0 else 1
            }
        )
    except Exception as e:
        logger.error(f"Error in get_gdpr_articles: {str(e)}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return format_response(error=str(e))

@router.get(
    "/gdpr/articles/{article_id}",
    summary="Dettagli articolo GDPR",
    response_description="Informazioni dettagliate su un articolo GDPR"
)
def get_article_by_id(
    article_id: int, 
    response: Response, 
    db: Session = Depends(get_db)
):
    """Recupera un articolo GDPR specifico tramite ID."""
    try:
        article = GDPRController.get_article(db, article_id)
        if not article:
            response.status_code = status.HTTP_404_NOT_FOUND
            return format_response(
                error=f"Articolo GDPR con ID {article_id} non trovato",
                message="Not Found"
            )
        return format_response(data=article)
    except Exception as e:
        logger.error(f"Error in get_article_by_id: {str(e)}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return format_response(error=str(e))

@router.get("/gdpr/articles/number/{article_number}")
def get_article_by_number(article_number: str, response: Response, db: Session = Depends(get_db)):
    """Recupera un articolo GDPR specifico tramite numero di articolo"""
    try:
        logger.info(f"Tentativo di recuperare articolo GDPR con numero={article_number}")
        article = GDPRController.get_article_by_number(db, article_number)
        if not article:
            response.status_code = status.HTTP_404_NOT_FOUND
            return format_response(
                error=f"Articolo GDPR numero {article_number} non trovato",
                message="Not Found"
            )
        return format_response(data=article)
    except Exception as e:
        logger.error(f"ERRORE nel recupero dell'articolo GDPR {article_number}: {str(e)}")
        logger.error(traceback.format_exc())
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return format_response(error=str(e))

@router.get("/gdpr/categories/{category}")
def get_articles_by_category(
    category: str, 
    response: Response,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Recupera articoli GDPR filtrati per categoria"""
    try:
        logger.info(f"Tentativo di recuperare articoli GDPR per categoria={category}")
        result = GDPRController.get_articles_by_category(db, category, skip=skip, limit=limit)
        return format_response(data=result)
    except Exception as e:
        logger.error(f"ERRORE nel recupero degli articoli GDPR per categoria {category}: {str(e)}")
        logger.error(traceback.format_exc())
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return format_response(error=str(e))

@router.get("/gdpr/search")
def search_articles(
    response: Response,
    query: str = Query(..., description="Termine di ricerca per gli articoli GDPR"),
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Cerca articoli GDPR in base a una query testuale"""
    try:
        logger.info(f"Tentativo di cercare articoli GDPR con query={query}")
        result = GDPRController.search_articles(db, query, skip=skip, limit=limit)
        return format_response(data=result)
    except Exception as e:
        logger.error(f"ERRORE nella ricerca degli articoli GDPR con query {query}: {str(e)}")
        logger.error(traceback.format_exc())
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return format_response(error=str(e))

@router.get("/gdpr/stats")
def get_gdpr_stats(response: Response, db: Session = Depends(get_db)):
    """Recupera statistiche sugli articoli GDPR"""
    try:
        logger.info("Tentativo di recuperare statistiche GDPR")
        result = GDPRController.get_gdpr_stats(db)
        return format_response(data=result)
    except Exception as e:
        logger.error(f"ERRORE nel recupero delle statistiche GDPR: {str(e)}")
        logger.error(traceback.format_exc())
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return format_response(error=str(e))