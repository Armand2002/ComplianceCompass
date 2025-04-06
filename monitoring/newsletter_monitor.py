# monitoring/newsletter_monitor.py
import time
import schedule
import logging
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from pathlib import Path
import sys
import os
import json

# Aggiungi la directory root al path per import
current_dir = Path(__file__).parent
root_dir = current_dir.parent
sys.path.append(str(root_dir))

from sqlalchemy.orm import Session
from sqlalchemy import func
from src.db.session import engine
from src.models.newsletter import NewsletterSubscription, NewsletterIssue

# Configurazione
CONFIG_FILE = current_dir / "monitor_config.json"
LOG_DIR = root_dir / "logs"
LOG_FILE = LOG_DIR / f"newsletter_monitor_{datetime.now().strftime('%Y%m%d')}.log"

# Assicurati che le directory esistano
LOG_DIR.mkdir(exist_ok=True)

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(filename=LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("newsletter_monitor")

def load_config():
    """Carica configurazione dal file JSON"""
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        else:
            # Configurazione di default
            config = {
                "alert_email": "admin@compliancecompass.app",
                "alert_thresholds": {
                    "inactive_percentage": 10,  # Allarme se percentuale inattivi > 10%
                    "verification_rate": 60,    # Allarme se tasso verifica < 60%
                    "send_failure_rate": 5      # Allarme se tasso fallimento invio > 5%
                },
                "smtp": {
                    "server": "smtp.example.com",
                    "port": 587,
                    "username": "alerter@compliancecompass.app",
                    "password": "your_password_here",
                    "from": "alerter@compliancecompass.app"
                }
            }
            # Salva configurazione di default
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
            return config
    except Exception as e:
        logger.error(f"Errore caricamento configurazione: {e}")
        sys.exit(1)

def send_alert_email(subject, message, config):
    """Invia email di allarme"""
    try:
        msg = MIMEMultipart()
        msg['From'] = config['smtp']['from']
        msg['To'] = config['alert_email']
        msg['Subject'] = f"ALERT: {subject}"
        
        msg.attach(MIMEText(message, 'plain'))
        
        context = ssl.create_default_context()
        with smtplib.SMTP(config['smtp']['server'], config['smtp']['port']) as server:
            server.starttls(context=context)
            server.login(config['smtp']['username'], config['smtp']['password'])
            server.send_message(msg)
            
        logger.info(f"Email di allarme inviata: {subject}")
    except Exception as e:
        logger.error(f"Errore invio email di allarme: {e}")

def check_newsletter_health():
    """Verifica salute del sistema newsletter"""
    logger.info("Esecuzione controllo salute newsletter")
    config = load_config()
    
    with Session(engine) as db:
        try:
            # 1. Statistiche iscrizioni
            total_subscriptions = db.query(func.count(NewsletterSubscription.id)).scalar() or 0
            active_subscriptions = db.query(func.count(NewsletterSubscription.id)).filter(
                NewsletterSubscription.is_active == True
            ).scalar() or 0
            verified_subscriptions = db.query(func.count(NewsletterSubscription.id)).filter(
                NewsletterSubscription.is_verified == True
            ).scalar() or 0
            
            logger.info(f"Totale iscrizioni: {total_subscriptions}")
            logger.info(f"Iscrizioni attive: {active_subscriptions}")
            logger.info(f"Iscrizioni verificate: {verified_subscriptions}")
            
            # 2. Calcolo metriche
            inactive_percentage = 0
            verification_rate = 0
            
            if total_subscriptions > 0:
                inactive_percentage = ((total_subscriptions - active_subscriptions) / total_subscriptions) * 100
                verification_rate = (verified_subscriptions / total_subscriptions) * 100
            
            # 3. Statistiche invii recenti
            recent_date = datetime.utcnow() - timedelta(days=7)
            recent_issues = db.query(NewsletterIssue).filter(
                NewsletterIssue.sent_at != None,
                NewsletterIssue.sent_at >= recent_date
            ).all()
            
            # 4. Allarmi
            alerts = []
            
            # 4.1 Percentuale inattivi
            if inactive_percentage > config['alert_thresholds']['inactive_percentage']:
                alerts.append(f"ATTENZIONE: Percentuale iscritti inattivi alta ({inactive_percentage:.1f}%)")
            
            # 4.2 Tasso di verifica
            if verification_rate < config['alert_thresholds']['verification_rate'] and total_subscriptions > 10:
                alerts.append(f"ATTENZIONE: Tasso di verifica basso ({verification_rate:.1f}%)")
            
            # Invia allarmi se presenti
            if alerts:
                message = "Report salute sistema newsletter:\n\n"
                message += f"Totale iscritti: {total_subscriptions}\n"
                message += f"Iscritti attivi: {active_subscriptions}\n"
                message += f"Iscritti verificati: {verified_subscriptions}\n"
                message += f"Percentuale inattivi: {inactive_percentage:.1f}%\n"
                message += f"Tasso verifica: {verification_rate:.1f}%\n\n"
                message += "PROBLEMI RILEVATI:\n"
                message += "\n".join(alerts)
                
                send_alert_email("Problemi sistema newsletter", message, config)
            
        except Exception as e:
            logger.error(f"Errore durante controllo salute: {e}")
            send_alert_email(
                "Errore monitoraggio newsletter", 
                f"Si è verificato un errore durante il monitoraggio del sistema newsletter: {str(e)}", 
                config
            )

def main():
    """Funzione principale del monitor"""
    logger.info("Avvio monitor sistema newsletter")
    
    # Esegui subito un controllo iniziale
    check_newsletter_health()
    
    # Pianifica controlli giornalieri
    schedule.every().day.at("08:00").do(check_newsletter_health)
    
    # Loop principale
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)
        except KeyboardInterrupt:
            logger.info("Interruzione monitor richiesta")
            break
        except Exception as e:
            logger.error(f"Errore nel loop principale: {e}")
            time.sleep(300)  # Recupera dopo 5 minuti in caso di errore

if __name__ == "__main__":
    main()