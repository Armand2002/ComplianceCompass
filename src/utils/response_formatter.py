"""Utility per formattare le risposte API in modo coerente."""
from typing import Dict, Any, Optional

def format_response(
    data: Any = None,
    error: Optional[str] = None,
    message: str = "Success"
) -> Dict[str, Any]:
    """
    Formatta le risposte API in modo coerente.
    
    Args:
        data: Dati da restituire
        error: Eventuale messaggio di errore
        message: Messaggio di successo
        
    Returns:
        Risposta API formattata
    """
    response = {
        "status": "error" if error else "success",
        "message": error if error else message
    }
    
    if data is not None:
        response["data"] = data
        
    return response