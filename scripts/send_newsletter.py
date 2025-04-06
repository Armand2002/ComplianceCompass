# scripts/send_newsletter.py
import os
import sys
import argparse
import logging
from datetime import datetime
from pathlib import Path

# Aggiungi la directory root al path per import
current_dir = Path(__file__).parent
root_dir = current_dir.parent
sys.path.append(str(root_dir))

from sqlalchemy.orm import Session
from src.db.session import engine, get_db
from src.services.newsletter_service import NewsletterService
from src.models.newsletter import NewsletterIssue, NewsletterSubscription
from src.controllers.user_controller import UserController

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(filename=f"logs/newsletter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("newsletter_sender")

def setup_argparse():
    parser = argparse.ArgumentParser(description='Invia newsletter agli iscritti')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--issue-id', type=int, help='ID della newsletter da inviare')
    group.add_argument('--create', action='store_true', help='Crea una nuova newsletter')
    parser.add_argument('--subject', type=str, help='Oggetto della newsletter (richiesto con --create)')
    parser.add_argument('--content-file', type=str, help='File HTML con il contenuto (richiesto con --create)')
    parser.add_argument('--admin-id', type=int, help='ID dell\'admin che invia (richiesto con --create)')
    parser.add_argument('--test-email', type=str, help='Invia solo a questa email per testing')
    parser.add_argument('--dry-run', action='store_true', help='Simula invio senza spedire effettivamente')
    return parser.parse_args()

def create_newsletter(db: Session, args):
    if not args.subject or not args.content_file or not args.admin_id:
        logger.error("Per creare una newsletter sono richiesti: --subject, --content-file e --admin-id")
        sys.exit(1)
        
    try:
        with open(args.content_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Verifica esistenza admin
        user_service = UserController()
        admin = user_service.get_user_by_id(db, args.admin_id)
        if not admin or not admin.is_admin:
            logger.error(f"ID admin non valido o utente non è amministratore: {args.admin_id}")
            sys.exit(1)
            
        # Crea newsletter
        newsletter_service = NewsletterService()
        result = newsletter_service.create_newsletter_issue(
            db, args.subject, content, args.admin_id
        )
        
        if not result.get("success"):
            logger.error(f"Errore creazione newsletter: {result.get('message')}")
            sys.exit(1)
            
        issue = result["issue"]
        logger.info(f"Newsletter creata con ID: {issue.id}")
        return issue.id
    except Exception as e:
        logger.exception("Errore durante la creazione della newsletter")
        sys.exit(1)

def send_newsletter(db: Session, issue_id: int, test_email: str = None, dry_run: bool = False):
    try:
        newsletter_service = NewsletterService()
        
        # Verifica esistenza newsletter
        issue = db.query(NewsletterIssue).filter(NewsletterIssue.id == issue_id).first()
        if not issue:
            logger.error(f"Newsletter con ID {issue_id} non trovata")
            sys.exit(1)
            
        # Modalità test - invio a singola email
        if test_email:
            logger.info(f"MODALITÀ TEST: invio solo a {test_email}")
            # Verifica se l'email è già registrata
            subscription = db.query(NewsletterSubscription).filter(
                NewsletterSubscription.email == test_email
            ).first()
            
            if not subscription:
                logger.warning(f"Email di test {test_email} non trovata negli iscritti. Creazione temporanea...")
                subscription = NewsletterSubscription(
                    email=test_email,
                    is_active=True,
                    is_verified=True
                )
                
            if dry_run:
                logger.info(f"DRY RUN: simulazione invio a {test_email}")
                logger.info(f"Newsletter: {issue.subject}")
                logger.info(f"Contenuto: {issue.content[:100]}...")
                return
                
            # Invio solo all'email di test
            sent = newsletter_service.email_service.send_email(
                to_email=test_email,
                subject=issue.subject,
                template_name="newsletter/issue_template.html",
                template_data={
                    "content": issue.content,
                    "subject": issue.subject,
                    "unsubscribe_url": f"/newsletter/unsubscribe?email={test_email}",
                    "email": test_email,
                    "current_year": datetime.now().year
                }
            )
            
            if sent:
                logger.info(f"Email di test inviata con successo a {test_email}")
            else:
                logger.error(f"Errore nell'invio dell'email di test a {test_email}")
            return
        
        # Modalità dry run - solo simulazione
        if dry_run:
            active_count = db.query(NewsletterSubscription).filter(
                NewsletterSubscription.is_active == True,
                NewsletterSubscription.is_verified == True
            ).count()
            logger.info(f"DRY RUN: simulazione invio a {active_count} iscritti")
            logger.info(f"Newsletter: {issue.subject}")
            logger.info(f"Contenuto: {issue.content[:100]}...")
            return
            
        # Invio effettivo
        result = newsletter_service.send_newsletter_issue(db, issue_id)
        
        if not result.get("success"):
            logger.error(f"Errore invio newsletter: {result.get('message')}")
            sys.exit(1)
            
        logger.info(f"Newsletter inviata con successo: {result.get('message')}")
        logger.info(f"Dettagli: {result.get('successful_sends')} invii riusciti, {result.get('failed_sends')} falliti")
        
        if result.get('failed_emails'):
            logger.warning(f"Email fallite: {', '.join(result.get('failed_emails'))}")
    except Exception as e:
        logger.exception("Errore durante l'invio della newsletter")
        sys.exit(1)

def main():
    args = setup_argparse()
    
    # Ensure logs directory
    os.makedirs('logs', exist_ok=True)
    
    with Session(engine) as db:
        issue_id = args.issue_id
        
        # Se richiesta creazione
        if args.create:
            issue_id = create_newsletter(db, args)
            
        # Invio newsletter
        send_newsletter(db, issue_id, args.test_email, args.dry_run)
    
    logger.info("Operazione completata")

if __name__ == "__main__":
    main()