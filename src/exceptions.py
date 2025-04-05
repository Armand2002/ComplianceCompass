# src/exceptions.py
"""
Modulo per le eccezioni personalizzate del dominio.

Questo modulo definisce eccezioni custom per gestire 
casi specifici di errore nell'applicazione.
"""

class DomainException(Exception):
    """
    Eccezione base per errori di dominio.
    
    Fornisce un meccanismo standardizzato per la gestione 
    degli errori specifici dell'applicazione.
    
    Attributes:
        message (str): Messaggio descrittivo dell'errore
        error_code (str, optional): Codice identificativo dell'errore
    """
    def __init__(self, message: str, error_code: str = None):
        """
        Inizializza l'eccezione di dominio.
        
        Args:
            message (str): Messaggio descrittivo dell'errore
            error_code (str, optional): Codice identificativo dell'errore
        """
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

    def __str__(self):
        """
        Restituisce una rappresentazione testuale dell'eccezione.
        
        Returns:
            str: Descrizione completa dell'eccezione
        """
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class ServiceUnavailableException(DomainException):
    """
    Eccezione sollevata quando un servizio esterno non è disponibile.
    
    Utilizzata per gestire scenari in cui servizi come Elasticsearch, 
    API esterne o database non sono raggiungibili.
    """
    def __init__(self, service_name: str, reason: str = None):
        """
        Inizializza l'eccezione per servizio non disponibile.
        
        Args:
            service_name (str): Nome del servizio non disponibile
            reason (str, optional): Ragione specifica dell'indisponibilità
        """
        message = f"Servizio '{service_name}' non disponibile"
        if reason:
            message += f": {reason}"
        
        super().__init__(message, error_code="SERVICE_UNAVAILABLE")
        self.service_name = service_name


class DataIntegrityException(DomainException):
    """
    Eccezione sollevata in caso di violazioni di integrità dei dati.
    
    Utilizzata quando si verificano problemi di coerenza o 
    validazione dei dati.
    """
    def __init__(self, entity: str, details: str = None):
        """
        Inizializza l'eccezione di integrità dati.
        
        Args:
            entity (str): Nome dell'entità con problemi di integrità
            details (str, optional): Dettagli specifici dell'errore
        """
        message = f"Violazione di integrità per {entity}"
        if details:
            message += f": {details}"
        
        super().__init__(message, error_code="DATA_INTEGRITY_ERROR")
        self.entity = entity


class AuthorizationException(DomainException):
    """
    Eccezione sollevata per problemi di autorizzazione.
    
    Gestisce scenari di accesso non autorizzato o 
    mancanza di permessi.
    """
    def __init__(self, user: str, action: str, reason: str = None):
        """
        Inizializza l'eccezione di autorizzazione.
        
        Args:
            user (str): Identificativo dell'utente
            action (str): Azione che l'utente ha tentato di eseguire
            reason (str, optional): Ragione del diniego
        """
        message = f"Utente '{user}' non autorizzato a eseguire '{action}'"
        if reason:
            message += f": {reason}"
        
        super().__init__(message, error_code="AUTHORIZATION_DENIED")
        self.user = user
        self.action = action