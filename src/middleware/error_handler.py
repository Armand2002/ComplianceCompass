# src/middleware/error_handler.py
import logging
import uuid
import traceback
import time
from typing import Union, Dict, Any, Callable, Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
from pydantic import ValidationError

from src.config import settings
from src.exceptions import DomainException

logger = logging.getLogger(__name__)

class ErrorDetail:
    """Struttura standardizzata per i dettagli degli errori."""
    
    def __init__(
        self, 
        message: str,
        error_type: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        error_id: Optional[str] = None
    ):
        self.message = message
        self.error_type = error_type
        self.error_code = error_code
        self.details = details or {}
        self.error_id = error_id or str(uuid.uuid4())
        self.timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte l'errore in dizionario."""
        result = {
            "message": self.message,
            "error_id": self.error_id,
            "timestamp": self.timestamp
        }
        
        # Aggiungi campi opzionali
        if self.error_code:
            result["error_code"] = self.error_code
            
        # In development, aggiungi tipo errore e dettagli
        if settings.ENVIRONMENT != "production":
            result["error_type"] = self.error_type
            if self.details:
                result["details"] = self.details
        
        return result
    
    @staticmethod
    def from_exception(exc: Exception, error_code: Optional[str] = None) -> 'ErrorDetail':
        """Crea un ErrorDetail da un'eccezione."""
        error_type = type(exc).__name__
        
        # Estrai dettagli in base al tipo di eccezione
        details = {}
        
        if isinstance(exc, RequestValidationError):
            details["validation_errors"] = [
                {
                    "loc": " -> ".join([str(loc) for loc in err["loc"]]),
                    "msg": err["msg"],
                    "type": err["type"]
                }
                for err in exc.errors()
            ]
        
        if isinstance(exc, DomainException) and hasattr(exc, 'details'):
            details["domain_details"] = exc.details
        
        return ErrorDetail(
            message=str(exc),
            error_type=error_type,
            error_code=error_code or getattr(exc, 'error_code', None),
            details=details
        )

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
    
    error_detail = ErrorDetail(
        message=exc.detail if isinstance(exc.detail, str) else str(exc.detail),
        error_type="HTTPException",
        error_code=f"HTTP_{exc.status_code}"
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": error_detail.to_dict()}
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
    error_detail = ErrorDetail.from_exception(exc, error_code="VALIDATION_ERROR")
    
    logger.warning(
        f"Errore di validazione: {error_detail.error_id} - "
        f"Path: {request.url.path} - "
        f"Errori: {len(error_detail.details.get('validation_errors', []))}"
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": error_detail.to_dict()}
    )

async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    """
    Handler specifico per errori di integrità del database.
    
    Args:
        request (Request): Richiesta HTTP
        exc (IntegrityError): Eccezione di integrità SQL
        
    Returns:
        JSONResponse: Risposta JSON con dettagli dell'errore
    """
    error_detail = ErrorDetail(
        message="Errore di integrità dei dati",
        error_type="IntegrityError",
        error_code="DB_INTEGRITY_ERROR"
    )
    
    # Log dettagliato
    logger.error(
        f"Errore integrità database: {error_detail.error_id} - "
        f"Path: {request.url.path}",
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"error": error_detail.to_dict()}
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
    # Gestione specifica per tipi diversi di errori database
    if isinstance(exc, IntegrityError):
        return await integrity_error_handler(request, exc)
    
    if isinstance(exc, OperationalError):
        # Errori di connessione o operativi
        error_code = "DB_OPERATIONAL_ERROR"
        message = "Errore operativo del database"
    else:
        # Altri errori database
        error_code = "DB_ERROR"
        message = "Errore interno del database"
    
    error_detail = ErrorDetail(
        message=message,
        error_type=type(exc).__name__,
        error_code=error_code
    )
    
    # Log dettagliato
    logger.error(
        f"Errore database: {error_detail.error_id} - "
        f"Path: {request.url.path}",
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": error_detail.to_dict()}
    )

async def domain_exception_handler(request: Request, exc: DomainException) -> JSONResponse:
    """
    Handler per le eccezioni di dominio personalizzate.
    
    Args:
        request (Request): Richiesta HTTP
        exc (DomainException): Eccezione di dominio
        
    Returns:
        JSONResponse: Risposta JSON con dettagli dell'errore
    """
    # Mappa il codice HTTP in base al tipo di eccezione di dominio
    status_code = status.HTTP_400_BAD_REQUEST
    
    if isinstance(exc, exc.__class__) and hasattr(exc, 'status_code'):
        status_code = exc.status_code
    
    error_detail = ErrorDetail.from_exception(exc)
    
    # Log con livello appropriato
    if status_code >= 500:
        logger.error(
            f"Errore di dominio: {error_detail.error_id} - "
            f"Path: {request.url.path} - {exc.message}",
            exc_info=True
        )
    else:
        logger.warning(
            f"Errore di dominio: {error_detail.error_id} - "
            f"Path: {request.url.path} - {exc.message}"
        )
    
    return JSONResponse(
        status_code=status_code,
        content={"error": error_detail.to_dict()}
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
    error_detail = ErrorDetail.from_exception(exc, error_code="VALIDATION_ERROR")
    
    errors = []
    for error in exc.errors():
        location = " -> ".join([str(loc) for loc in error["loc"]])
        errors.append({
            "location": location,
            "message": error["msg"],
            "type": error["type"]
        })
    
    error_detail.details["validation_errors"] = errors
    
    logger.warning(
        f"Errore validazione Pydantic: {error_detail.error_id} - "
        f"Path: {request.url.path} - Errori: {len(errors)}"
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": error_detail.to_dict()}
    )

async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler per le eccezioni generiche non gestite altrove.
    
    Args:
        request (Request): Richiesta HTTP
        exc (Exception): Eccezione generica
        
    Returns:
        JSONResponse: Risposta JSON con dettagli dell'errore
    """
    error_detail = ErrorDetail.from_exception(exc, error_code="INTERNAL_SERVER_ERROR")
    
    # Log dettagliato dell'errore
    logger.error(
        f"Eccezione non gestita: {error_detail.error_id} - "
        f"Path: {request.url.path} - "
        f"Tipo: {type(exc).__name__} - "
        f"Messaggio: {str(exc)}",
        exc_info=True
    )
    
    # In ambiente di produzione, nasconde i dettagli dell'errore
    if settings.ENVIRONMENT == "production":
        error_detail.message = "Si è verificato un errore interno"
        error_detail.details = {}
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": error_detail.to_dict()}
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
    app.exception_handler(DomainException)(domain_exception_handler)
    app.exception_handler(Exception)(general_exception_handler)