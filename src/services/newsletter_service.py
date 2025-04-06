# src/services/newsletter_service.py
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import secrets
import logging

from src.models.newsletter import NewsletterSubscription, NewsletterIssue
from src.services.email_service import EmailService

logger = logging.getLogger(__name__)

class NewsletterService:
    """
    Servizio per la gestione delle iscrizioni alla newsletter.
    
    Gestisce tutte le operazioni relative alle iscrizioni, invio email di verifica,
    e gestione delle newsletter.
    """
    def __init__(self):
        self.email_service = EmailService()
    
    def subscribe(self, db: Session, email: str) -> Dict[str, Any]:
        """
        Iscrive un utente alla newsletter.
        
        Args:
            db: Sessione database
            email: Email dell'utente da iscrivere
            
        Returns:
            Dizionario con informazioni sull'iscrizione e token di verifica
        """
        try:
            # Verifica se l'email è già registrata
            existing = db.query(NewsletterSubscription).filter(
                NewsletterSubscription.email == email
            ).first()
            
            if existing:
                if existing.is_verified:
                    # Email già verificata
                    return {
                        "success": False,
                        "message": "Email già iscritta alla newsletter",
                        "subscription": existing,
                        "already_subscribed": True
                    }
                else:
                    # Email registrata ma non verificata - genera nuovo token
                    verification_token = secrets.token_urlsafe(32)
                    existing.verification_token = verification_token
                    existing.last_updated_at = datetime.utcnow()
                    db.commit()
                    
                    # Invia nuova email di verifica
                    self.send_verification_email(email, verification_token)
                    
                    return {
                        "success": True,
                        "message": "Email già registrata. Nuova email di verifica inviata.",
                        "subscription": existing,
                        "requires_verification": True
                    }
            
            # Crea nuova iscrizione
            verification_token = secrets.token_urlsafe(32)
            subscription = NewsletterSubscription(
                email=email,
                verification_token=verification_token,
                is_active=True,
                is_verified=False
            )
            
            db.add(subscription)
            db.commit()
            db.refresh(subscription)
            
            # Invia email di verifica
            self.send_verification_email(email, verification_token)
            
            return {
                "success": True,
                "message": "Iscrizione creata. Email di verifica inviata.",
                "subscription": subscription,
                "requires_verification": True
            }
            
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Errore di integrità durante l'iscrizione: {str(e)}")
            return {
                "success": False,
                "message": "Errore durante l'iscrizione. Email potrebbe essere già registrata.",
                "error": str(e)
            }
        except Exception as e:
            db.rollback()
            logger.error(f"Errore durante l'iscrizione: {str(e)}")
            return {
                "success": False,
                "message": "Errore durante l'iscrizione",
                "error": str(e)
            }
    
    def unsubscribe(self, db: Session, email: str) -> Dict[str, Any]:
        """
        Cancella l'iscrizione di un utente dalla newsletter.
        
        Args:
            db: Sessione database
            email: Email dell'utente da disiscrivere
            
        Returns:
            Dizionario con esito dell'operazione
        """
        try:
            subscription = db.query(NewsletterSubscription).filter(
                NewsletterSubscription.email == email
            ).first()
            
            if not subscription:
                return {
                    "success": False,
                    "message": "Email non trovata"
                }
            
            # Disattiva l'iscrizione (soft delete)
            subscription.is_active = False
            subscription.last_updated_at = datetime.utcnow()
            db.commit()
            
            # Invia email di conferma cancellazione
            self.email_service.send_email(
                to_email=email,
                subject="Cancellazione dalla newsletter completata",
                template_name="newsletter/unsubscribe_confirmation.html",
                template_data={
                    "email": email,
                    "unsubscribe_date": datetime.now().strftime("%d/%m/%Y")
                }
            )
            
            return {
                "success": True,
                "message": "Iscrizione cancellata con successo"
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Errore durante la cancellazione: {str(e)}")
            return {
                "success": False,
                "message": "Errore durante la cancellazione",
                "error": str(e)
            }
    
    def verify_subscription(self, db: Session, email: str, token: str) -> Dict[str, Any]:
        """
        Verifica un'iscrizione alla newsletter tramite token.
        
        Args:
            db: Sessione database
            email: Email dell'utente
            token: Token di verifica
            
        Returns:
            Dizionario con esito della verifica
        """
        try:
            subscription = db.query(NewsletterSubscription).filter(
                NewsletterSubscription.email == email,
                NewsletterSubscription.verification_token == token
            ).first()
            
            if not subscription:
                return {
                    "success": False,
                    "message": "Combinazione email/token non valida"
                }
            
            if subscription.is_verified:
                return {
                    "success": True,
                    "message": "Email già verificata",
                    "already_verified": True
                }
            
            # Aggiorna stato iscrizione
            subscription.is_verified = True
            subscription.verification_token = None  # Rimuove token dopo verifica
            subscription.last_updated_at = datetime.utcnow()
            db.commit()
            
            # Invia email di benvenuto
            self.send_welcome_email(email)
            
            return {
                "success": True,
                "message": "Email verificata con successo"
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Errore durante la verifica: {str(e)}")
            return {
                "success": False,
                "message": "Errore durante la verifica",
                "error": str(e)
            }
    
    def get_subscription_status(self, db: Session, email: str) -> Dict[str, Any]:
        """
        Ottiene lo stato di iscrizione di un'email.
        
        Args:
            db: Sessione database
            email: Email da verificare
            
        Returns:
            Dizionario con lo stato dell'iscrizione
        """
        try:
            subscription = db.query(NewsletterSubscription).filter(
                NewsletterSubscription.email == email
            ).first()
            
            if not subscription:
                return {
                    "subscribed": False,
                    "message": "Email non iscritta"
                }
            
            return {
                "subscribed": True,
                "is_active": subscription.is_active,
                "is_verified": subscription.is_verified,
                "subscribed_at": subscription.subscribed_at.isoformat(),
                "message": "Email trovata"
            }
            
        except Exception as e:
            logger.error(f"Errore durante il controllo stato: {str(e)}")
            return {
                "success": False,
                "message": "Errore durante il controllo stato",
                "error": str(e)
            }
    
    def send_verification_email(self, email: str, token: str) -> bool:
        """
        Invia un'email di verifica per l'iscrizione alla newsletter.
        
        Args:
            email: Email destinatario
            token: Token di verifica
            
        Returns:
            True se l'invio è riuscito, False altrimenti
        """
        try:
            verification_url = f"/newsletter/verify?email={email}&token={token}"
            
            # Utilizza il sistema di template esistente
            return self.email_service.send_email(
                to_email=email,
                subject="Verifica la tua iscrizione alla newsletter",
                template_name="newsletter/verification_email.html",
                template_data={
                    "verification_url": verification_url,
                    "email": email,
                    "token": token
                }
            )
        except Exception as e:
            logger.error(f"Errore durante l'invio email di verifica: {str(e)}")
            return False
    
    def send_welcome_email(self, email: str) -> bool:
        """
        Invia un'email di benvenuto dopo la verifica.
        
        Args:
            email: Email destinatario
            
        Returns:
            True se l'invio è riuscito, False altrimenti
        """
        try:
            manage_url = f"/newsletter/manage?email={email}"
            
            # Utilizza il sistema di template esistente
            return self.email_service.send_email(
                to_email=email,
                subject="Benvenuto nella newsletter di ComplianceCompass",
                template_name="newsletter/welcome_email.html",
                template_data={
                    "manage_url": manage_url,
                    "email": email
                }
            )
        except Exception as e:
            logger.error(f"Errore durante l'invio email di benvenuto: {str(e)}")
            return False
    
    def get_active_subscriptions(self, db: Session, skip: int = 0, limit: int = 100) -> List[NewsletterSubscription]:
        """
        Ottiene la lista delle iscrizioni attive e verificate.
        Versione ottimizzata che seleziona solo i campi necessari.
        
        Args:
            db: Sessione database
            skip: Numero di record da saltare (paginazione)
            limit: Numero massimo di record da restituire
            
        Returns:
            Lista di iscrizioni attive
        """
        # Selezioniamo solo i campi necessari per l'invio delle newsletter
        return db.query(NewsletterSubscription.id, NewsletterSubscription.email).filter(
            NewsletterSubscription.is_active == True,
            NewsletterSubscription.is_verified == True
        ).offset(skip).limit(limit).all()
    
    def create_newsletter_issue(self, db: Session, subject: str, content: str, created_by_id: int) -> Dict[str, Any]:
        """
        Crea una nuova edizione della newsletter.
        
        Args:
            db: Sessione database
            subject: Oggetto della newsletter
            content: Contenuto HTML della newsletter
            created_by_id: ID dell'utente che ha creato la newsletter
            
        Returns:
            Dizionario con informazioni sulla newsletter creata
        """
        try:
            issue = NewsletterIssue(
                subject=subject,
                content=content,
                created_by_id=created_by_id
            )
            
            db.add(issue)
            db.commit()
            db.refresh(issue)
            
            return {
                "success": True,
                "message": "Newsletter creata con successo",
                "issue": issue
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Errore durante la creazione della newsletter: {str(e)}")
            return {
                "success": False,
                "message": "Errore durante la creazione della newsletter",
                "error": str(e)
            }
    
    def send_newsletter_issue(self, db: Session, issue_id: int) -> Dict[str, Any]:
        """
        Invia una newsletter a tutti gli iscritti attivi.
        
        Args:
            db: Sessione database
            issue_id: ID della newsletter da inviare
            
        Returns:
            Dizionario con esito dell'invio
        """
        try:
            # Recupera la newsletter
            issue = db.query(NewsletterIssue).filter(
                NewsletterIssue.id == issue_id
            ).first()
            
            if not issue:
                return {
                    "success": False,
                    "message": "Newsletter non trovata"
                }
            
            if issue.sent_at:
                return {
                    "success": False,
                    "message": "Newsletter già inviata",
                    "sent_at": issue.sent_at.isoformat()
                }
            
            # Recupera tutti gli iscritti attivi
            active_subscriptions = self.get_active_subscriptions(db)
            
            # Conta successi e fallimenti
            success_count = 0
            failed_emails = []
            
            # Invia a ogni iscritto
            for subscription in active_subscriptions:
                try:
                    sent = self.email_service.send_email(
                        to_email=subscription.email,
                        subject=issue.subject,
                        template_name="newsletter/issue_template.html",
                        template_data={
                            "content": issue.content,
                            "unsubscribe_url": f"/newsletter/unsubscribe?email={subscription.email}",
                            "email": subscription.email
                        }
                    )
                    
                    if sent:
                        success_count += 1
                    else:
                        failed_emails.append(subscription.email)
                        
                except Exception as e:
                    logger.error(f"Errore invio a {subscription.email}: {str(e)}")
                    failed_emails.append(subscription.email)
            
            # Aggiorna stato newsletter
            issue.sent_at = datetime.utcnow()
            db.commit()
            
            return {
                "success": True,
                "message": f"Newsletter inviata a {success_count} iscritti",
                "total_subscribers": len(active_subscriptions),
                "successful_sends": success_count,
                "failed_sends": len(failed_emails),
                "failed_emails": failed_emails
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Errore durante l'invio della newsletter: {str(e)}")
            return {
                "success": False,
                "message": "Errore durante l'invio della newsletter",
                "error": str(e)
            }