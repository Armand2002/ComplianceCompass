# src/utils/email.py
import logging
from jinja2 import Template
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
    
    with open('templates/reset_password.html') as f:
        template = Template(f.read())
    html_content = template.render(username=username, reset_url=reset_url, app_name=settings.APP_NAME)
    
    subject = f"Reset Password - {settings.APP_NAME}"
    
    try:
        return email_service.send_email(to_email, subject, html_content)
    except Exception as e:
        logger.error(f"Errore nell'invio dell'email di reset password: {str(e)}")
        return False