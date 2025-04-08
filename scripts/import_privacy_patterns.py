#!/usr/bin/env python
"""
Script semplificato per importare privacy patterns da un file CSV.
Evita dipendenze circolari e problemi con campi del database.

Uso:
    python -m scripts.import_basic_patterns privacy_patterns.csv
"""
import os
import sys
import csv
import logging
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text

# Aggiungi la directory principale al path per importare i moduli
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db.session import SessionLocal
from src.models.privacy_pattern import PrivacyPattern
from src.models.gdpr_model import GDPRArticle
from src.models.pbd_principle import PbDPrinciple
from src.models.iso_phase import ISOPhase
from src.models.vulnerability import Vulnerability
from src.models.user_model import User

# Configurazione logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clean_str(value):
    """Pulisce e converte i valori in stringhe."""
    if not value:
        return ""
    return str(value).strip()

def split_values(value, delimiter=','):
    """Divide una stringa in valori multipli."""
    if not value:
        return []
    return [v.strip() for v in value.split(delimiter) if v.strip()]

def import_patterns(file_path, admin_id=1, delimiter=';'):
    """
    Importa i pattern dal file CSV nel database.
    
    Args:
        file_path: Percorso del file CSV
        admin_id: ID dell'utente admin da impostare come creatore
        delimiter: Separatore utilizzato nel CSV
    """
    db = SessionLocal()
    
    try:
        # Verifica che l'utente admin esista
        admin = db.query(User).filter(User.id == admin_id).first()
        if not admin:
            logger.error(f"Utente admin con ID {admin_id} non trovato!")
            return False
        
        logger.info(f"Admin trovato: {admin.username}")
        
        # Contatori
        patterns_created = 0
        patterns_skipped = 0
        
        # Prova diverse codifiche
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as csvfile:
                    # Prova a leggere la prima riga per verificare se la codifica funziona
                    csvfile.readline()
                    csvfile.seek(0)  # Torna all'inizio del file
                    
                    logger.info(f"Codifica rilevata: {encoding}")
                    
                    # Leggi il CSV
                    reader = csv.DictReader(csvfile, delimiter=delimiter)
                    
                    # Mostra le colonne trovate
                    logger.info(f"Colonne trovate: {', '.join(reader.fieldnames)}")
                    
                    for row_index, row in enumerate(reader, start=2):
                        title = clean_str(row.get('Pattern', ''))
                        
                        if not title:
                            logger.warning(f"Riga {row_index}: Titolo mancante, salto")
                            patterns_skipped += 1
                            continue
                        
                        # Verifica se il pattern esiste già
                        existing_pattern = db.query(PrivacyPattern).filter(PrivacyPattern.title == title).first()
                        if existing_pattern:
                            logger.warning(f"Pattern '{title}' già esistente, salto")
                            patterns_skipped += 1
                            continue
                        
                        # Fase 1: Crea il pattern di base (senza relazioni)
                        pattern = PrivacyPattern()
                        pattern.title = title
                        pattern.description = clean_str(row.get('Description Pattern', ''))
                        pattern.context = clean_str(row.get('Context Pattern', ''))
                        pattern.problem = "Extracted from description"
                        pattern.solution = "See examples for solutions"
                        pattern.consequences = clean_str(row.get('Examples', ''))
                        pattern.strategy = clean_str(row.get('Strategies', ''))
                        pattern.mvc_component = clean_str(row.get('Collocazione MVC', ''))
                        pattern.created_by_id = admin_id
                        pattern.created_at = datetime.utcnow()
                        pattern.updated_at = datetime.utcnow()
                        
                        # Salva il pattern per ottenere l'ID
                        db.add(pattern)
                        db.commit()
                        logger.info(f"Pattern di base '{title}' creato")
                        
                        # Fase 2: Aggiungi le relazioni GDPR
                        try:
                            gdpr_text = clean_str(row.get('Article GDPR Compliance with the Pattern', ''))
                            gdpr_refs = split_values(gdpr_text)
                            
                            for ref in gdpr_refs:
                                # Estrai il numero dell'articolo (es. "Article 32" -> "32")
                                article_num = ref.replace("Article", "").strip()
                                if "�" in article_num:
                                    article_num = article_num.split("�")[0].strip()
                                
                                gdpr = db.query(GDPRArticle).filter(GDPRArticle.number == article_num).first()
                                if gdpr:
                                    db.execute(
                                        text("INSERT INTO pattern_gdpr_association (pattern_id, gdpr_id) VALUES (:pattern_id, :gdpr_id)"),
                                        {"pattern_id": pattern.id, "gdpr_id": gdpr.id}
                                    )
                                    logger.info(f"  Aggiunto riferimento GDPR: Articolo {article_num}")
                                else:
                                    logger.warning(f"  Articolo GDPR '{article_num}' non trovato nel database")
                        except Exception as e:
                            logger.warning(f"  Errore aggiungendo riferimenti GDPR: {str(e)}")
                            db.rollback()
                        
                        # Fase 3: Aggiungi le relazioni PbD
                        try:
                            pbd_text = clean_str(row.get('Privacy By Design Principles', ''))
                            pbd_refs = split_values(pbd_text, delimiter=',')
                            
                            for ref in pbd_refs:
                                pbd = db.query(PbDPrinciple).filter(PbDPrinciple.name == ref).first()
                                if pbd:
                                    db.execute(
                                        text("INSERT INTO pattern_pbd_association (pattern_id, pbd_id) VALUES (:pattern_id, :pbd_id)"),
                                        {"pattern_id": pattern.id, "pbd_id": pbd.id}
                                    )
                                    logger.info(f"  Aggiunto principio PbD: {ref}")
                                else:
                                    logger.warning(f"  Principio PbD '{ref}' non trovato nel database")
                        except Exception as e:
                            logger.warning(f"  Errore aggiungendo principi PbD: {str(e)}")
                        
                        # Fase 4: Aggiungi le relazioni ISO - CORREZIONE
                        try:
                            iso_text = clean_str(row.get('ISO 9241-210 Phase', ''))
                            iso_refs = split_values(iso_text, delimiter=',')
                            
                            for ref in iso_refs:
                                iso = db.query(ISOPhase).filter(ISOPhase.name == ref).first()
                                if iso:
                                    db.execute(
                                        text("INSERT INTO pattern_iso_association (pattern_id, iso_id) VALUES (:pattern_id, :iso_id)"),
                                        {"pattern_id": pattern.id, "iso_id": iso.id}  # Qui c'era l'errore: "pbd_id" invece di "iso_id"
                                    )
                                    logger.info(f"  Aggiunta fase ISO: {ref}")
                                else:
                                    logger.warning(f"  Fase ISO '{ref}' non trovata nel database")
                        except Exception as e:
                            logger.warning(f"  Errore aggiungendo fasi ISO: {str(e)}")
                        
                        # Fase 5: Aggiungi le relazioni Vulnerabilità
                        try:
                            vuln_text = clean_str(row.get('CWE Top 25 Most Dangerous Software Weaknesses OWASP Categories Associated', ''))
                            vuln_refs = split_values(vuln_text, delimiter=',')
                            
                            for ref in vuln_refs:
                                # Estrai il codice CWE (es. "CWE-306: ..." -> "CWE-306")
                                cwe_code = ref.split(':')[0].strip() if ':' in ref else ref
                                
                                vuln = db.query(Vulnerability).filter(Vulnerability.cwe_id == cwe_code).first()
                                if vuln:
                                    db.execute(
                                        text("INSERT INTO pattern_vulnerability_association (pattern_id, vulnerability_id) VALUES (:pattern_id, :vulnerability_id)"),
                                        {"pattern_id": pattern.id, "vulnerability_id": vuln.id}
                                    )
                                    logger.info(f"  Aggiunta vulnerabilità: {cwe_code}")
                                else:
                                    logger.warning(f"  Vulnerabilità '{cwe_code}' non trovata nel database")
                        except Exception as e:
                            logger.warning(f"  Errore aggiungendo vulnerabilità: {str(e)}")
                        
                        db.commit()
                        patterns_created += 1
                        logger.info(f"Pattern '{title}' importato con successo (con relazioni)")
                    
                    # Se arriviamo qui, la codifica funziona
                    logger.info(f"Importazione completata: {patterns_created} pattern creati, {patterns_skipped} saltati")
                    return True
            except Exception as e:
                logger.warning(f"Errore con la codifica {encoding}: {str(e)}")
        
        logger.error("Nessuna codifica ha funzionato per il file")
        return False
    
    except Exception as e:
        logger.error(f"Errore generale: {str(e)}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Importa privacy patterns da CSV")
    parser.add_argument("file_path", help="Percorso del file CSV")
    parser.add_argument("--admin-id", type=int, default=1, help="ID dell'utente admin (default: 1)")
    parser.add_argument("--delimiter", default=";", help="Separatore CSV (default: ';')")
    
    args = parser.parse_args()
    
    logger.info("Avvio importazione...")
    success = import_patterns(args.file_path, args.admin_id, args.delimiter)
    
    if success:
        logger.info("Importazione completata con successo!")
        sys.exit(0)
    else:
        logger.error("Importazione fallita.")
        sys.exit(1)