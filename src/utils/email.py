# Nuovo file src/utils/email.py
import logging
from src.config import settings
from src.services.email_service import EmailService

logger = logging.getLogger(__name__)
email_service = EmailService()

def send_password_reset_email(to_email: str, username: str, token: str) -> bool:
    """
    Invia un'email per il reset della password.
    
    Args:
        to_email (str): Indirizzo email del destinatario
        username (str): Username del destinatario
        token (str): Token di reset
        
    Returns:
        bool: True se l'email è stata inviata con successo
    """
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    
    html_content = f"""
    <html>
    <body>
        <h2>Reset Password - {settings.APP_NAME}</h2>
        <p>Ciao {username},</p>
        <p>Hai richiesto il reset della tua password. Clicca sul link seguente per impostare una nuova password:</p>
        <p><a href="{reset_url}">Reset Password</a></p>
        <p>Se non hai richiesto questo reset, ignora questa email.</p>
        <p>Il link scadrà tra 24 ore.</p>
        <p>Grazie,<br>Il team di {settings.APP_NAME}</p>
    </body>
    </html>
    """
    
    subject = f"Reset Password - {settings.APP_NAME}"
    
    try:
        return email_service.send_email(to_email, subject, html_content)
    except Exception as e:
        logger.error(f"Errore nell'invio dell'email di reset password: {str(e)}")
        return False