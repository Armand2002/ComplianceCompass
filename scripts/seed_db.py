#!/usr/bin/env python
# scripts/seed_db.py
"""
Script per popolare il database con dati iniziali.

Questo script crea:
1. Un utente admin (se non esiste già)
2. Articoli GDPR di base
3. Principi Privacy by Design
4. Fasi ISO
5. Vulnerabilità comuni
6. Alcuni pattern di privacy di esempio

Uso: python -m scripts.seed_db
"""
import logging
import sys
import os
from datetime import datetime
from sqlalchemy.exc import IntegrityError

# Aggiungi la directory principale al path per importare i moduli
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.user_model import User, UserRole
from src.models.gdpr_model import GDPRArticle
from src.models.pbd_principle import PbDPrinciple
from src.models.iso_phase import ISOPhase
from src.models.vulnerability import Vulnerability, SeverityLevel
from src.models.privacy_pattern import PrivacyPattern
from src.utils.password import get_password_hash
from src.db.session import SessionLocal
from src.services.search_service import SearchService

# Configurazione logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def seed_admin_user(db):
    """Crea un utente admin se non esiste già."""
    ADMIN_EMAIL = "admin@compliancecompass.com"
    ADMIN_USERNAME = "admin"
    ADMIN_PASSWORD = "admin123"  # In produzione, usa una password sicura e variabili d'ambiente
    
    # Verifica se esiste già l'utente admin
    admin = db.query(User).filter(User.email == ADMIN_EMAIL).first()
    
    if not admin:
        logger.info(f"Creazione utente admin ({ADMIN_EMAIL})...")
        admin = User(
            email=ADMIN_EMAIL,
            username=ADMIN_USERNAME,
            hashed_password=get_password_hash(ADMIN_PASSWORD),
            full_name="Administrator",
            role=UserRole.ADMIN,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(admin)
        db.commit()
        logger.info("Utente admin creato con successo!")
        return admin
    else:
        logger.info("L'utente admin esiste già.")
        return admin

def seed_gdpr_articles(db):
    """Crea articoli GDPR di base."""
    logger.info("Creazione articoli GDPR...")
    
    gdpr_articles = [
        {
            "number": "5.1.a",
            "title": "Principi di liceità, correttezza e trasparenza",
            "content": "I dati personali sono trattati in modo lecito, corretto e trasparente nei confronti dell'interessato.",
            "summary": "Il trattamento dei dati deve essere legittimo, equo e trasparente.",
            "category": "Principi"
        },
        {
            "number": "5.1.b",
            "title": "Limitazione della finalità",
            "content": "I dati personali sono raccolti per finalità determinate, esplicite e legittime.",
            "summary": "I dati devono essere raccolti solo per scopi specifici dichiarati.",
            "category": "Principi"
        },
        {
            "number": "5.1.c",
            "title": "Minimizzazione dei dati",
            "content": "I dati personali sono adeguati, pertinenti e limitati a quanto necessario rispetto alle finalità.",
            "summary": "Raccogliere solo i dati necessari per le finalità dichiarate.",
            "category": "Principi"
        },
        {
            "number": "25.1",
            "title": "Protezione dei dati fin dalla progettazione",
            "content": "Tenendo conto dello stato dell'arte e dei costi di attuazione, nonché della natura, dell'ambito di applicazione, del contesto e delle finalità del trattamento, come anche dei rischi per i diritti e le libertà delle persone fisiche, il titolare del trattamento mette in atto misure tecniche e organizzative adeguate per garantire che siano trattati, per impostazione predefinita, solo i dati personali necessari per ogni specifica finalità del trattamento.",
            "summary": "Implementare misure tecniche e organizzative per garantire la protezione dei dati personali fin dalla fase di progettazione.",
            "category": "Principi"
        },
        {
            "number": "25.2",
            "title": "Protezione dei dati per impostazione predefinita",
            "content": "Il titolare del trattamento mette in atto misure tecniche e organizzative adeguate per garantire che siano trattati, per impostazione predefinita, solo i dati personali necessari per ogni specifica finalità del trattamento.",
            "summary": "Le impostazioni predefinite del sistema devono essere configurate per massimizzare la privacy.",
            "category": "Principi"
        },
        {
            "number": "32.1",
            "title": "Sicurezza del trattamento",
            "content": "Tenendo conto dello stato dell'arte e dei costi di attuazione, nonché della natura, dell'oggetto, del contesto e delle finalità del trattamento, come anche del rischio di varia probabilità e gravità per i diritti e le libertà delle persone fisiche, il titolare del trattamento e il responsabile del trattamento mettono in atto misure tecniche e organizzative adeguate per garantire un livello di sicurezza adeguato al rischio.",
            "summary": "Implementare misure di sicurezza appropriate per proteggere i dati personali.",
            "category": "Sicurezza"
        }
    ]
    
    for article_data in gdpr_articles:
        article = db.query(GDPRArticle).filter(GDPRArticle.number == article_data["number"]).first()
        
        if not article:
            article = GDPRArticle(**article_data)
            db.add(article)
            logger.info(f"Aggiunto articolo GDPR {article_data['number']}")
    
    db.commit()
    logger.info("Articoli GDPR creati con successo!")

def seed_pbd_principles(db):
    """Crea principi Privacy by Design."""
    logger.info("Creazione principi Privacy by Design...")
    
    pbd_principles = [
        {
            "name": "Proattivo non reattivo",
            "description": "Il Privacy by Design previene i problemi di privacy prima che si verifichino, non interviene dopo le violazioni.",
            "guidance": "Implementare analisi dei rischi per la privacy nelle prime fasi di progettazione del sistema."
        },
        {
            "name": "Privacy come impostazione predefinita",
            "description": "La massima privacy è garantita per impostazione predefinita, senza richiedere azioni da parte dell'utente.",
            "guidance": "Configurare i sistemi con le impostazioni più restrittive per la privacy come default."
        },
        {
            "name": "Privacy incorporata nella progettazione",
            "description": "La privacy è integrata nella progettazione e nell'architettura dei sistemi IT e delle pratiche aziendali.",
            "guidance": "Considerare la privacy come requisito funzionale durante la fase di progettazione dell'architettura."
        },
        {
            "name": "Funzionalità completa",
            "description": "Privacy by Design cerca soluzioni positive somma-somma, non compromessi che degradano la funzionalità.",
            "guidance": "Dimostrare che la privacy può coesistere con altre funzionalità e requisiti di sistema."
        },
        {
            "name": "Sicurezza end-to-end",
            "description": "La privacy è protetta durante l'intero ciclo di vita dei dati, dalla raccolta alla distruzione.",
            "guidance": "Implementare controlli di sicurezza adeguati in ogni fase del trattamento dei dati."
        },
        {
            "name": "Visibilità e trasparenza",
            "description": "Le operazioni sono documentate e comunicate chiaramente a tutte le parti interessate.",
            "guidance": "Creare documentazione chiara sul trattamento dei dati e renderla accessibile agli utenti."
        },
        {
            "name": "Rispetto per la privacy dell'utente",
            "description": "Il design incentrato sull'utente mantiene gli interessi dell'individuo al centro.",
            "guidance": "Dare agli utenti opzioni semplici e chiare per il controllo della loro privacy."
        }
    ]
    
    for principle_data in pbd_principles:
        principle = db.query(PbDPrinciple).filter(PbDPrinciple.name == principle_data["name"]).first()
        
        if not principle:
            principle = PbDPrinciple(**principle_data)
            db.add(principle)
            logger.info(f"Aggiunto principio PbD: {principle_data['name']}")
    
    db.commit()
    logger.info("Principi Privacy by Design creati con successo!")

def seed_iso_phases(db):
    """Crea fasi ISO del ciclo di vita dello sviluppo software."""
    logger.info("Creazione fasi ISO...")
    
    iso_phases = [
        {
            "name": "Pianificazione",
            "standard": "ISO/IEC 27001",
            "description": "Definizione degli obiettivi, dei requisiti e della pianificazione del progetto.",
            "order": 1
        },
        {
            "name": "Analisi dei requisiti",
            "standard": "ISO/IEC 27001",
            "description": "Raccolta e analisi dei requisiti funzionali e non funzionali, inclusi i requisiti di privacy e sicurezza.",
            "order": 2
        },
        {
            "name": "Progettazione",
            "standard": "ISO/IEC 27001",
            "description": "Definizione dell'architettura del sistema e delle soluzioni tecniche per soddisfare i requisiti.",
            "order": 3
        },
        {
            "name": "Implementazione",
            "standard": "ISO/IEC 27001",
            "description": "Sviluppo del codice e delle componenti del sistema secondo le specifiche di progettazione.",
            "order": 4
        },
        {
            "name": "Testing",
            "standard": "ISO/IEC 27001",
            "description": "Verifica del sistema per assicurarsi che soddisfi i requisiti e sia privo di vulnerabilità.",
            "order": 5
        },
        {
            "name": "Deployment",
            "standard": "ISO/IEC 27001",
            "description": "Rilascio del sistema nell'ambiente di produzione.",
            "order": 6
        },
        {
            "name": "Manutenzione",
            "standard": "ISO/IEC 27001",
            "description": "Attività di supporto, aggiornamento e miglioramento continuo del sistema.",
            "order": 7
        }
    ]
    
    for phase_data in iso_phases:
        phase = db.query(ISOPhase).filter(ISOPhase.name == phase_data["name"]).first()
        
        if not phase:
            phase = ISOPhase(**phase_data)
            db.add(phase)
            logger.info(f"Aggiunta fase ISO: {phase_data['name']}")
    
    db.commit()
    logger.info("Fasi ISO create con successo!")

def seed_vulnerabilities(db):
    """Crea vulnerabilità comuni."""
    logger.info("Creazione vulnerabilità comuni...")
    
    vulnerabilities = [
        {
            "name": "Cross-Site Scripting (XSS)",
            "description": "Vulnerabilità che permette agli aggressori di iniettare script client-side dannosi in pagine web visualizzate da altri utenti.",
            "severity": SeverityLevel.HIGH,
            "category": "Web Application",
            "cwe_id": "CWE-79"
        },
        {
            "name": "SQL Injection",
            "description": "Vulnerabilità che consente agli aggressori di inserire codice SQL dannoso nelle query, potenzialmente accedendo a dati sensibili.",
            "severity": SeverityLevel.CRITICAL,
            "category": "Database",
            "cwe_id": "CWE-89"
        },
        {
            "name": "Esposizione di dati sensibili",
            "description": "Inadeguata protezione di dati personali o sensibili, che potrebbero essere accessibili a persone non autorizzate.",
            "severity": SeverityLevel.HIGH,
            "category": "Privacy",
            "cwe_id": "CWE-200"
        },
        {
            "name": "Controllo di accesso difettoso",
            "description": "Implementazione inadeguata di meccanismi di controllo che permette accessi non autorizzati a funzionalità o dati.",
            "severity": SeverityLevel.HIGH,
            "category": "Sicurezza",
            "cwe_id": "CWE-284"
        },
        {
            "name": "Configurazione di sicurezza errata",
            "description": "Configurazioni di sicurezza inadeguate che possono portare a vulnerabilità evitabili.",
            "severity": SeverityLevel.MEDIUM,
            "category": "Configurazione",
            "cwe_id": "CWE-1021"
        },
        {
            "name": "Tracciamento eccessivo dell'utente",
            "description": "Raccolta di dati di tracciamento dell'utente oltre quanto necessario per le funzionalità dichiarate.",
            "severity": SeverityLevel.MEDIUM,
            "category": "Privacy",
            "cwe_id": "CWE-359"
        }
    ]
    
    for vuln_data in vulnerabilities:
        vuln = db.query(Vulnerability).filter(Vulnerability.name == vuln_data["name"]).first()
        
        if not vuln:
            vuln = Vulnerability(**vuln_data)
            db.add(vuln)
            logger.info(f"Aggiunta vulnerabilità: {vuln_data['name']}")
    
    db.commit()
    logger.info("Vulnerabilità create con successo!")

def seed_privacy_patterns(db, admin_user):
    """Crea alcuni pattern di privacy di esempio."""
    logger.info("Creazione pattern di privacy di esempio...")
    
    # Ottieni relazioni
    gdpr_articles = {article.number: article for article in db.query(GDPRArticle).all()}
    pbd_principles = {principle.name: principle for principle in db.query(PbDPrinciple).all()}
    iso_phases = {phase.name: phase for phase in db.query(ISOPhase).all()}
    vulnerabilities = {vuln.name: vuln for vuln in db.query(Vulnerability).all()}
    
    patterns = [
        {
            "title": "Minimizzazione dei dati",
            "description": "Principio che prevede la raccolta e l'utilizzo solo dei dati personali strettamente necessari per raggiungere una finalità specifica.",
            "context": "Applicabile in contesti dove vengono raccolti dati personali dagli utenti, come form di registrazione, procedure di checkout, o raccolta di feedback.",
            "problem": "La raccolta eccessiva di dati personali aumenta i rischi di privacy e viola il principio di minimizzazione dei dati del GDPR.",
            "solution": "Identificare i dati minimi necessari per ogni finalità e limitare la raccolta solo a questi. Eliminare campi non essenziali dai form e dalle procedure di raccolta dati.",
            "consequences": "Riduzione dei rischi di privacy, maggiore conformità al GDPR, maggiore fiducia degli utenti. Possibili limitazioni nell'analisi dei dati e nel marketing.",
            "strategy": "Minimize",
            "mvc_component": "Model",
            "created_by_id": admin_user.id,
            "gdpr_references": ["5.1.c", "25.2"],
            "pbd_references": ["Privacy come impostazione predefinita", "Privacy incorporata nella progettazione"],
            "iso_references": ["Analisi dei requisiti", "Progettazione"],
            "vulnerability_references": ["Esposizione di dati sensibili", "Tracciamento eccessivo dell'utente"]
        },
        {
            "title": "Consenso informato",
            "description": "Pattern che garantisce che gli utenti forniscano un consenso libero, specifico, informato e inequivocabile per il trattamento dei loro dati personali.",
            "context": "Applicabile quando si raccolgono dati personali e si richiede il consenso dell'utente per il trattamento, come in form di registrazione o cookie banner.",
            "problem": "Ottenere un consenso valido richiede che l'utente sia adeguatamente informato e abbia la possibilità di esprimere liberamente la propria scelta.",
            "solution": "Implementare meccanismi di consenso chiari, con informazioni dettagliate sulle finalità del trattamento e opzioni granulari per diverse tipologie di trattamento.",
            "consequences": "Maggiore trasparenza, maggiore controllo per gli utenti, miglioramento della conformità normativa. Possibile aumento della complessità dell'interfaccia utente.",
            "strategy": "Inform",
            "mvc_component": "View",
            "created_by_id": admin_user.id,
            "gdpr_references": ["5.1.a", "25.1"],
            "pbd_references": ["Rispetto per la privacy dell'utente", "Visibilità e trasparenza"],
            "iso_references": ["Progettazione", "Implementazione"],
            "vulnerability_references": ["Configurazione di sicurezza errata"]
        },
        {
            "title": "Pseudonimizzazione",
            "description": "Tecnica che sostituisce gli identificatori diretti con pseudonimi, mantenendo l'utilità dei dati ma riducendo i rischi per la privacy.",
            "context": "Applicabile in sistemi che elaborano dati personali per finalità di analisi, ricerca o per la condivisione con terze parti.",
            "problem": "L'uso di identificatori diretti nei dataset aumenta i rischi di identificazione e violazione della privacy degli interessati.",
            "solution": "Sostituire gli identificatori diretti (come nome, email, ID) con pseudonimi o codici, conservando separatamente la tabella di mappatura.",
            "consequences": "Riduzione del rischio di identificazione, mantenimento dell'utilità dei dati per l'analisi, maggiore conformità al GDPR. Complessità aggiuntiva nella gestione dei dati.",
            "strategy": "Abstract",
            "mvc_component": "Model",
            "created_by_id": admin_user.id,
            "gdpr_references": ["25.1", "32.1"],
            "pbd_references": ["Sicurezza end-to-end", "Funzionalità completa"],
            "iso_references": ["Implementazione", "Testing"],
            "vulnerability_references": ["Esposizione di dati sensibili"]
        }
    ]
    
    for pattern_data in patterns:
        # Verifica se il pattern esiste già
        pattern = db.query(PrivacyPattern).filter(PrivacyPattern.title == pattern_data["title"]).first()
        
        if not pattern:
            # Estrai riferimenti
            gdpr_refs = pattern_data.pop("gdpr_references", [])
            pbd_refs = pattern_data.pop("pbd_references", [])
            iso_refs = pattern_data.pop("iso_references", [])
            vuln_refs = pattern_data.pop("vulnerability_references", [])
            
            # Crea pattern
            pattern = PrivacyPattern(**pattern_data)
            
            # Aggiungi relazioni
            for ref in gdpr_refs:
                if ref in gdpr_articles:
                    pattern.gdpr_articles.append(gdpr_articles[ref])
            
            for ref in pbd_refs:
                if ref in pbd_principles:
                    pattern.pbd_principles.append(pbd_principles[ref])
            
            for ref in iso_refs:
                if ref in iso_phases:
                    pattern.iso_phases.append(iso_phases[ref])
            
            for ref in vuln_refs:
                if ref in vulnerabilities:
                    pattern.vulnerabilities.append(vulnerabilities[ref])
            
            db.add(pattern)
            logger.info(f"Aggiunto pattern: {pattern_data['title']}")
    
    db.commit()
    logger.info("Pattern di privacy creati con successo!")
    
    # Indicizza i pattern in Elasticsearch
    try:
        search_service = SearchService()
        if search_service.es:
            for pattern in db.query(PrivacyPattern).all():
                search_service.index_pattern(pattern)
            logger.info("Pattern indicizzati in Elasticsearch con successo!")
        else:
            logger.warning("Elasticsearch non disponibile. I pattern non sono stati indicizzati.")
    except Exception as e:
        logger.error(f"Errore nell'indicizzazione dei pattern: {str(e)}")


def main():
    """Funzione principale per eseguire tutte le operazioni di seeding."""
    logger.info("Avvio popolamento database...")
    
    # Crea la sessione del database
    db = SessionLocal()
    
    try:
        # Crea utente admin
        admin_user = seed_admin_user(db)
        
        # Popola entità di base
        seed_gdpr_articles(db)
        seed_pbd_principles(db)
        seed_iso_phases(db)
        seed_vulnerabilities(db)
        
        # Popola pattern di privacy
        seed_privacy_patterns(db, admin_user)
        
        logger.info("Popolamento database completato con successo!")
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Errore di integrità nel database: {str(e)}")
    except Exception as e:
        db.rollback()
        logger.error(f"Errore durante il popolamento del database: {str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    main()