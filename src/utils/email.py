# src/utils/email.py
import logging
import os
from jinja2 import FileSystemLoader, Environment
from src.config import settings
from src.services.email_service import EmailService

logger = logging.getLogger(__name__)
email_service = EmailService()

# Usa un percorso assoluto invece di PackageLoader
templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
template_env = Environment(loader=FileSystemLoader(templates_dir))

def get_template(template_name):
    try:
        return template_env.get_template(template_name)
    except Exception as e:
        print(f"Impossibile caricare il template {template_name}: {str(e)}")
        return None

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
    
    template = get_template('reset_password.html')
    if not template:
        return False
    
    html_content = template.render(username=username, reset_url=reset_url, app_name=settings.APP_NAME)
    
    subject = f"Reset Password - {settings.APP_NAME}"
    
    try:
        return email_service.send_email(to_email, subject, html_content)
    except Exception as e:
        logger.error(f"Errore nell'invio dell'email di reset password: {str(e)}")
        return False