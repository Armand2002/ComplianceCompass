# src/services/email_service.py
import logging
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape

from src.config import settings
from src.models.notification import NotificationType

logger = logging.getLogger(__name__)

class EmailService:
    """
    Servizio per l'invio di email.
    
    Gestisce la creazione e l'invio di email agli utenti.
    """
    
    def __init__(self):
        """Inizializza il servizio email con i template Jinja2."""
        try:
            templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates/emails")
            self.env = Environment(
                loader=FileSystemLoader(templates_dir),
                autoescape=select_autoescape(['html', 'xml'])
            )
        except Exception as e:
            logger.warning(f"Impossibile caricare i template email: {str(e)}")
            self.env = None
    
    def send_email(
        self, 
        to_email: str, 
        subject: str, 
        html_content: str, 
        text_content: Optional[str] = None
    ) -> bool:
        """
        Invia un'email.
        
        Args:
            to_email (str): Indirizzo email del destinatario
            subject (str): Oggetto dell'email
            html_content (str): Contenuto HTML dell'email
            text_content (str, optional): Contenuto testuale dell'email
            
        Returns:
            bool: True se l'invio è riuscito, False altrimenti
        """
        # Non inviare email se in modalità di sviluppo
        if settings.ENVIRONMENT == "development" and not settings.DEBUG:
            logger.info(f"Email non inviata in ambiente di sviluppo: {subject} a {to_email}")
            return True
        
        # Salta se non sono configurati i parametri SMTP
        if not settings.SMTP_SERVER or not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
            logger.warning("Parametri SMTP non configurati. Email non inviata.")
            return False
        
        try:
            # Crea messaggio multipart
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = settings.EMAIL_FROM
            msg['To'] = to_email
            
            # Aggiungi contenuto testuale (fallback)
            if text_content:
                msg.attach(MIMEText(text_content, 'plain'))
            else:
                # Se non è fornito un contenuto testuale, estrai testo dall'HTML
                text = html_content.replace('<br>', '\n').replace('</p>', '\n\n')
                # Rimuovi tutti i tag HTML
                import re
                text = re.sub(r'<[^>]*>', '', text)
                msg.attach(MIMEText(text, 'plain'))
            
            # Aggiungi contenuto HTML
            msg.attach(MIMEText(html_content, 'html'))
            
            # Invia email
            with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
                server.ehlo()
                server.starttls()
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                server.send_message(msg)
            
            logger.info(f"Email inviata con successo a {to_email}: {subject}")
            return True
        except Exception as e:
            logger.error(f"Errore nell'invio dell'email a {to_email}: {str(e)}")
            return False
    
    def send_notification_email(
        self, 
        to_email: str, 
        subject: str, 
        message: str,
        notification_type: NotificationType = NotificationType.INFO
    ) -> bool:
        """
        Invia un'email di notifica.
        
        Args:
            to_email (str): Indirizzo email del destinatario
            subject (str): Oggetto dell'email
            message (str): Messaggio della notifica
            notification_type (NotificationType): Tipo di notifica
            
        Returns:
            bool: True se l'invio è riuscito, False altrimenti
        """
        try:
            if self.env:
                template = self.env.get_template('notification.html')
                html_content = template.render(
                    subject=subject,
                    message=message,
                    notification_type=notification_type.value,
                    app_name=settings.APP_NAME,
                    frontend_url=settings.FRONTEND_URL
                )
            else:
                # Template semplice se Jinja2 non è disponibile
                html_content = f"""
                <html>
                <body>
                    <h2>{subject}</h2>
                    <p>{message}</p>
                    <p>Accedi a <a href="{settings.FRONTEND_URL}">{settings.APP_NAME}</a> per maggiori dettagli.</p>
                </body>
                </html>
                """
            
            return self.send_email(to_email, subject, html_content)
        except Exception as e:
            logger.error(f"Errore nella creazione dell'email di notifica: {str(e)}")
            return False
    
    def send_welcome_email(self, to_email: str, username: str) -> bool:
        """
        Invia un'email di benvenuto a un nuovo utente.
        
        Args:
            to_email (str): Indirizzo email del destinatario
            username (str): Nome utente
            
        Returns:
            bool: True se l'invio è riuscito, False altrimenti
        """
        try:
            if self.env:
                template = self.env.get_template('welcome.html')
                html_content = template.render(
                    username=username,
                    app_name=settings.APP_NAME,
                    frontend_url=settings.FRONTEND_URL
                )
            else:
                # Template semplice se Jinja2 non è disponibile
                html_content = f"""
                <html>
                <body>
                    <h2>Benvenuto su {settings.APP_NAME}!</h2>
                    <p>Ciao {username},</p>
                    <p>Grazie per esserti registrato. Siamo felici di averti con noi!</p>
                    <p>Accedi a <a href="{settings.FRONTEND_URL}">{settings.APP_NAME}</a> per iniziare a esplorare.</p>
                </body>
                </html>
                """
            
            subject = f"Benvenuto su {settings.APP_NAME}"
            return self.send_email(to_email, subject, html_content)
        except Exception as e:
            logger.error(f"Errore nella creazione dell'email di benvenuto: {str(e)}")
            return False
    
    def send_password_reset_email(self, to_email: str, reset_token: str, username: str) -> bool:
        """
        Invia un'email per il reset della password.
        
        Args:
            to_email (str): Indirizzo email del destinatario
            reset_token (str): Token per il reset della password
            username (str): Nome utente
            
        Returns:
            bool: True se l'invio è riuscito, False altrimenti
        """
        try:
            reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
            
            if self.env:
                template = self.env.get_template('password_reset.html')
                html_content = template.render(
                    username=username,
                    reset_url=reset_url,
                    app_name=settings.APP_NAME
                )
            else:
                # Template semplice se Jinja2 non è disponibile
                html_content = f"""
                <html>
                <body>
                    <h2>Reset Password - {settings.APP_NAME}</h2>
                    <p>Ciao {username},</p>
                    <p>Hai richiesto il reset della tua password. Clicca sul link seguente per impostare una nuova password:</p>
                    <p><a href="{reset_url}">Reset Password</a></p>
                    <p>Se non hai richiesto questo reset, ignora questa email.</p>
                    <p>Il link scadrà tra 24 ore.</p>
                </body>
                </html>
                """
            
            subject = f"Reset Password - {settings.APP_NAME}"
            return self.send_email(to_email, subject, html_content)
        except Exception as e:
            logger.error(f"Errore nella creazione dell'email di reset password: {str(e)}")
            return False