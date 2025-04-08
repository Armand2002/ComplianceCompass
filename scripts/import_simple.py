#!/usr/bin/env python
"""
Script semplificato per importare privacy patterns da CSV usando SQL diretto.
Evita completamente i problemi di dipendenze circolari tra modelli ORM.

Uso:
    python -m scripts.import_simple privacy_patterns.csv
"""
import os
import sys
import csv
import logging
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

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
    Importa i pattern dal file CSV nel database usando SQL diretto.
    
    Args:
        file_path: Percorso del file CSV
        admin_id: ID dell'utente admin da impostare come creatore
        delimiter: Separatore utilizzato nel CSV
    """
    # Connessione diretta al DB per evitare problemi con ORM
    engine = create_engine('postgresql://postgres:postgres@db:5432/postgres')
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # Utilizzando ID admin
        logger.info(f"Utilizzando ID admin: {admin_id}")
        
        # Contatori
        patterns_created = 0
        patterns_skipped = 0
        
        # Prova diverse codifiche
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as csvfile:
                    # Prova a leggere la prima riga per verificare la codifica
                    csvfile.readline()
                    csvfile.seek(0)
                    
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
                        result = db.execute(
                            text("SELECT id FROM privacy_patterns WHERE title = :title"),
                            {"title": title}
                        )
                        if result.fetchone():
                            logger.warning(f"Pattern '{title}' già esistente, salto")
                            patterns_skipped += 1
                            continue
                        
                        # Prepara i dati del pattern
                        now = datetime.utcnow()
                        pattern_data = {
                            "title": title,
                            "description": clean_str(row.get('Description Pattern', '')),
                            "context": clean_str(row.get('Context Pattern', '')),
                            "problem": "Extracted from description",
                            "solution": "See examples for solutions",
                            "consequences": clean_str(row.get('Examples', '')),
                            "strategy": clean_str(row.get('Strategies', '')),
                            "mvc_component": clean_str(row.get('Collocazione MVC', '')),
                            "created_by_id": admin_id,
                            "created_at": now,
                            "updated_at": now
                        }
                        
                        # Fase 1: Inserisci il pattern di base usando SQL diretto
                        insert_result = db.execute(
                            text("""
                                INSERT INTO privacy_patterns 
                                (title, description, context, problem, solution, consequences, 
                                 strategy, mvc_component, created_by_id, created_at, updated_at)
                                VALUES 
                                (:title, :description, :context, :problem, :solution, :consequences,
                                 :strategy, :mvc_component, :created_by_id, :created_at, :updated_at)
                                RETURNING id
                            """),
                            pattern_data
                        )
                        pattern_id = insert_result.fetchone()[0]
                        db.commit()
                        logger.info(f"Pattern di base '{title}' creato con ID {pattern_id}")
                        
                        # Fase 2: Aggiungi le relazioni GDPR
                        try:
                            gdpr_text = clean_str(row.get('Article GDPR Compliance with the Pattern', ''))
                            gdpr_refs = split_values(gdpr_text)
                            
                            for ref in gdpr_refs:
                                # Estrai il numero dell'articolo (es. "Article 32" -> "32")
                                article_num = ref.replace("Article", "").strip()
                                if "�" in article_num:
                                    article_num = article_num.split("�")[0].strip()
                                
                                # Cerca l'articolo GDPR usando SQL diretto
                                gdpr_result = db.execute(
                                    text("SELECT id FROM gdpr_articles WHERE number = :number"),
                                    {"number": article_num}
                                )
                                gdpr = gdpr_result.fetchone()
                                
                                if gdpr:
                                    # Inserisci la relazione usando SQL diretto
                                    db.execute(
                                        text("INSERT INTO pattern_gdpr_association (pattern_id, gdpr_id) VALUES (:pattern_id, :gdpr_id)"),
                                        {"pattern_id": pattern_id, "gdpr_id": gdpr.id}
                                    )
                                    logger.info(f"  Aggiunto riferimento GDPR: Articolo {article_num}")
                                else:
                                    logger.warning(f"  Articolo GDPR '{article_num}' non trovato nel database")
                            db.commit()
                        except Exception as e:
                            db.rollback()
                            logger.warning(f"  Errore aggiungendo riferimenti GDPR: {str(e)}")
                        
                        # Fase 3: Aggiungi le relazioni PbD
                        try:
                            pbd_text = clean_str(row.get('Privacy By Design Principles', ''))
                            pbd_refs = split_values(pbd_text, delimiter=',')
                            
                            for ref in pbd_refs:
                                # Cerca il principio PbD usando SQL diretto
                                pbd_result = db.execute(
                                    text("SELECT id FROM pbd_principles WHERE name = :name"),
                                    {"name": ref}
                                )
                                pbd = pbd_result.fetchone()
                                
                                if pbd:
                                    # Inserisci la relazione usando SQL diretto
                                    db.execute(
                                        text("INSERT INTO pattern_pbd_association (pattern_id, pbd_id) VALUES (:pattern_id, :pbd_id)"),
                                        {"pattern_id": pattern_id, "pbd_id": pbd.id}
                                    )
                                    logger.info(f"  Aggiunto principio PbD: {ref}")
                                else:
                                    logger.warning(f"  Principio PbD '{ref}' non trovato nel database")
                            db.commit()
                        except Exception as e:
                            db.rollback()
                            logger.warning(f"  Errore aggiungendo principi PbD: {str(e)}")
                        
                        # Fase 4: Aggiungi le relazioni ISO
                        try:
                            iso_text = clean_str(row.get('ISO 9241-210 Phase', ''))
                            iso_refs = split_values(iso_text, delimiter=',')
                            
                            for ref in iso_refs:
                                # Cerca la fase ISO usando SQL diretto
                                iso_result = db.execute(
                                    text("SELECT id FROM iso_phases WHERE name = :name"),
                                    {"name": ref}
                                )
                                iso = iso_result.fetchone()
                                
                                if iso:
                                    # Inserisci la relazione usando SQL diretto
                                    db.execute(
                                        text("INSERT INTO pattern_iso_association (pattern_id, iso_id) VALUES (:pattern_id, :iso_id)"),
                                        {"pattern_id": pattern_id, "iso_id": iso.id}
                                    )
                                    logger.info(f"  Aggiunta fase ISO: {ref}")
                                else:
                                    logger.warning(f"  Fase ISO '{ref}' non trovata nel database")
                            db.commit()
                        except Exception as e:
                            db.rollback()
                            logger.warning(f"  Errore aggiungendo fasi ISO: {str(e)}")
                        
                        # Fase 5: Aggiungi le relazioni Vulnerabilità
                        try:
                            vuln_text = clean_str(row.get('CWE Top 25 Most Dangerous Software Weaknesses OWASP Categories Associated', ''))
                            vuln_refs = split_values(vuln_text, delimiter=',')
                            
                            for ref in vuln_refs:
                                # Estrai il codice CWE (es. "CWE-306: ..." -> "CWE-306")
                                cwe_code = ref.split(':')[0].strip() if ':' in ref else ref
                                
                                # Cerca la vulnerabilità usando SQL diretto
                                vuln_result = db.execute(
                                    text("SELECT id FROM vulnerabilities WHERE cwe_id = :cwe_id"),
                                    {"cwe_id": cwe_code}
                                )
                                vuln = vuln_result.fetchone()
                                
                                if vuln:
                                    # Inserisci la relazione usando SQL diretto
                                    db.execute(
                                        text("INSERT INTO pattern_vulnerability_association (pattern_id, vulnerability_id) VALUES (:pattern_id, :vulnerability_id)"),
                                        {"pattern_id": pattern_id, "vulnerability_id": vuln.id}
                                    )
                                    logger.info(f"  Aggiunta vulnerabilità: {cwe_code}")
                                else:
                                    logger.warning(f"  Vulnerabilità '{cwe_code}' non trovata nel database")
                            db.commit()
                        except Exception as e:
                            db.rollback()
                            logger.warning(f"  Errore aggiungendo vulnerabilità: {str(e)}")
                        
                        patterns_created += 1
                        logger.info(f"Pattern '{title}' importato con successo (con relazioni)")
                    
                    # Se arriviamo qui, la codifica funziona e l'importazione è completa
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
    
    parser = argparse.ArgumentParser(description="Importa privacy patterns da CSV usando SQL diretto")
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