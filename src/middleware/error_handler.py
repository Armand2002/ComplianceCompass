# src/middleware/error_handler.py
import logging
from typing import Union, Dict, Any, Callable
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError

logger = logging.getLogger(__name__)

async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    Handler per le eccezioni HTTP.
    
    Args:
        request (Request): Richiesta HTTP
        exc (StarletteHTTPException): Eccezione HTTP
        
    Returns:
        JSONResponse: Risposta JSON con dettagli dell'errore
    """
    logger.warning(f"HTTPException: {exc.status_code} - {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handler per le eccezioni di validazione.
    
    Args:
        request (Request): Richiesta HTTP
        exc (RequestValidationError): Eccezione di validazione
        
    Returns:
        JSONResponse: Risposta JSON con dettagli degli errori di validazione
    """
    errors = []
    for error in exc.errors():
        location = " -> ".join([str(loc) for loc in error["loc"]])
        errors.append({
            "location": location,
            "message": error["msg"],
            "type": error["type"]
        })
    
    logger.warning(f"Errore di validazione: {errors}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Errore di validazione dei dati",
            "errors": errors
        }
    )

async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """
    Handler per le eccezioni SQLAlchemy.
    
    Args:
        request (Request): Richiesta HTTP
        exc (SQLAlchemyError): Eccezione SQLAlchemy
        
    Returns:
        JSONResponse: Risposta JSON con dettagli dell'errore
    """
    logger.error(f"Errore database: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Errore interno del database"}
    )

async def pydantic_validation_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """
    Handler per le eccezioni di validazione Pydantic.
    
    Args:
        request (Request): Richiesta HTTP
        exc (ValidationError): Eccezione di validazione Pydantic
        
    Returns:
        JSONResponse: Risposta JSON con dettagli degli errori di validazione
    """
    errors = []
    for error in exc.errors():
        location = " -> ".join([str(loc) for loc in error["loc"]])
        errors.append({
            "location": location,
            "message": error["msg"],
            "type": error["type"]
        })
    
    logger.warning(f"Errore di validazione Pydantic: {errors}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Errore di validazione dei dati",
            "errors": errors
        }
    )

async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler per le eccezioni generiche.
    
    Args:
        request (Request): Richiesta HTTP
        exc (Exception): Eccezione generica
        
    Returns:
        JSONResponse: Risposta JSON con dettagli dell'errore
    """
    # Log dettagliato dell'errore
    logger.error(
        f"Eccezione non gestita di tipo {type(exc).__name__}: {str(exc)}",
        exc_info=True
    )
    
    # In ambiente di produzione, non esporre dettagli dell'errore
    from src.config import settings
    if settings.ENVIRONMENT == "production":
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Si è verificato un errore interno"}
        )
    else:
        # In ambiente di sviluppo, fornisci dettagli per il debug
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Si è verificato un errore interno",
                "error_type": type(exc).__name__,
                "error_message": str(exc)
            }
        )


def register_exception_handlers(app):
    """
    Registra tutti gli handler di eccezioni nell'applicazione.
    
    Args:
        app: Istanza dell'applicazione FastAPI
    """
    app.exception_handler(StarletteHTTPException)(http_exception_handler)
    app.exception_handler(RequestValidationError)(validation_exception_handler)
    app.exception_handler(SQLAlchemyError)(sqlalchemy_exception_handler)
    app.exception_handler(ValidationError)(pydantic_validation_handler)
    app.exception_handler(Exception)(general_exception_handler)