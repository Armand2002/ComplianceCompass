#!/usr/bin/env python
"""
Script completo che crea le tabelle necessarie e importa i privacy patterns.
Risolve tutti i problemi di dipendenze e tabelle mancanti.

Uso:
    python -m scripts.create_and_import privacy_patterns.csv
"""
import os
import sys
import csv
import logging
from datetime import datetime
from sqlalchemy import create_engine, text

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

def create_tables_and_import(file_path, delimiter=';'):
    """
    Crea le tabelle necessarie e importa i privacy patterns.
    
    Args:
        file_path: Percorso del file CSV
        delimiter: Separatore utilizzato nel CSV
    """
    # Connessione diretta al DB
    engine = create_engine('postgresql://postgres:postgres@db:5432/postgres')
    conn = engine.connect()
    
    try:
        # 1. Crea le tabelle necessarie se non esistono
        logger.info("Creazione tabelle...")
        
        # Tabella privacy_patterns
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS privacy_patterns (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL UNIQUE,
            description TEXT,
            context TEXT,
            problem TEXT,
            solution TEXT,
            consequences TEXT,
            strategy VARCHAR(255),
            mvc_component VARCHAR(255),
            created_by_id INTEGER,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        )
        """))
        
        # Tabella gdpr_articles
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS gdpr_articles (
            id SERIAL PRIMARY KEY,
            number VARCHAR(20) NOT NULL,
            title VARCHAR(255) NOT NULL,
            content TEXT,
            summary TEXT,
            category VARCHAR(100),
            chapter VARCHAR(100),
            is_key_article BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        )
        """))
        
        # Tabella pbd_principles
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS pbd_principles (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL UNIQUE,
            description TEXT,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        )
        """))
        
        # Tabella iso_phases
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS iso_phases (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL UNIQUE,
            description TEXT,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        )
        """))
        
        # Tabella vulnerabilities
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS vulnerabilities (
            id SERIAL PRIMARY KEY,
            cwe_id VARCHAR(50) NOT NULL UNIQUE,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            severity VARCHAR(50),
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        )
        """))
        
        # Tabelle di associazione
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS pattern_gdpr_association (
            pattern_id INTEGER REFERENCES privacy_patterns(id),
            gdpr_id INTEGER REFERENCES gdpr_articles(id),
            PRIMARY KEY (pattern_id, gdpr_id)
        )
        """))
        
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS pattern_pbd_association (
            pattern_id INTEGER REFERENCES privacy_patterns(id),
            pbd_id INTEGER REFERENCES pbd_principles(id),
            PRIMARY KEY (pattern_id, pbd_id)
        )
        """))
        
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS pattern_iso_association (
            pattern_id INTEGER REFERENCES privacy_patterns(id),
            iso_id INTEGER REFERENCES iso_phases(id),
            PRIMARY KEY (pattern_id, iso_id)
        )
        """))
        
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS pattern_vulnerability_association (
            pattern_id INTEGER REFERENCES privacy_patterns(id),
            vulnerability_id INTEGER REFERENCES vulnerabilities(id),
            PRIMARY KEY (pattern_id, vulnerability_id)
        )
        """))
        
        conn.commit()
        logger.info("Tabelle create con successo")
        
        # 2. Inserisci le entità di riferimento
        
        # GDPR Articles
        gdpr_articles = [
            {"number": "5.1.a", "title": "Principio di liceità, correttezza e trasparenza", "category": "Principi"},
            {"number": "5.1.b", "title": "Limitazione della finalità", "category": "Principi"},
            {"number": "5.1.c", "title": "Minimizzazione dei dati", "category": "Principi"},
            {"number": "25.1", "title": "Protezione dei dati fin dalla progettazione", "category": "Principi"},
            {"number": "25.2", "title": "Protezione per impostazione predefinita", "category": "Principi"},
            {"number": "32", "title": "Sicurezza del trattamento", "category": "Sicurezza"},
            {"number": "33", "title": "Notifica violazione dati personali", "category": "Sicurezza"},
            {"number": "34", "title": "Comunicazione violazione all'interessato", "category": "Sicurezza"},
            {"number": "35", "title": "Valutazione d'impatto", "category": "Obblighi"},
        ]
        
        for article in gdpr_articles:
            result = conn.execute(text("SELECT id FROM gdpr_articles WHERE number = :number"), {"number": article["number"]})
            if not result.fetchone():
                conn.execute(text("""
                INSERT INTO gdpr_articles (number, title, category) 
                VALUES (:number, :title, :category)
                """), article)
                logger.info(f"Articolo GDPR {article['number']} creato")
        
        # PbD Principles
        pbd_principles = [
            "Proactive not Reactive",
            "Privacy as the default setting",
            "Privacy Embedded into Design",
            "Full Functionality",
            "End-to-End Security",
            "Visibility and Transparency",
            "Respect for User Privacy"
        ]
        
        for principle in pbd_principles:
            result = conn.execute(text("SELECT id FROM pbd_principles WHERE name = :name"), {"name": principle})
            if not result.fetchone():
                conn.execute(text("INSERT INTO pbd_principles (name) VALUES (:name)"), {"name": principle})
                logger.info(f"Principio PbD '{principle}' creato")
        
        # ISO Phases
        iso_phases = [
            "7.2 Understanding and specifying the context of use",
            "7.3 Specify the requirements",
            "7.4 Producing design solutions",
            "7.5 Evaluating the design",
            "6. Plan the human-centered design process"
        ]
        
        for phase in iso_phases:
            result = conn.execute(text("SELECT id FROM iso_phases WHERE name = :name"), {"name": phase})
            if not result.fetchone():
                conn.execute(text("INSERT INTO iso_phases (name) VALUES (:name)"), {"name": phase})
                logger.info(f"Fase ISO '{phase}' creata")
        
        # CWE Vulnerabilities
        vulnerabilities = [
            {"cwe_id": "CWE-306", "name": "Missing Authentication for Critical Function", "severity": "High"},
            {"cwe_id": "CWE-798", "name": "Use of Hard-coded Credentials", "severity": "High"},
            {"cwe_id": "CWE-287", "name": "Improper Authentication", "severity": "High"},
            {"cwe_id": "CWE-269", "name": "Improper Privilege Management", "severity": "High"},
            {"cwe_id": "CWE-434", "name": "Unrestricted Upload of File with Dangerous Type", "severity": "High"},
            {"cwe_id": "CWE-22", "name": "Path Traversal", "severity": "High"},
            {"cwe_id": "CWE-862", "name": "Missing Authorization", "severity": "High"},
            {"cwe_id": "CWE-863", "name": "Incorrect Authorization", "severity": "High"},
            {"cwe_id": "CWE-276", "name": "Incorrect Default Permissions", "severity": "Medium"},
            {"cwe_id": "CWE-502", "name": "Deserialization of Untrusted Data", "severity": "High"},
            {"cwe_id": "CWE-20", "name": "Improper Input Validation", "severity": "High"},
            {"cwe_id": "CWE-79", "name": "Cross-site Scripting", "severity": "High"},
            {"cwe_id": "CWE-89", "name": "SQL Injection", "severity": "High"},
            {"cwe_id": "CWE-78", "name": "OS Command Injection", "severity": "High"},
            {"cwe_id": "CWE-77", "name": "Command Injection", "severity": "High"},
            {"cwe_id": "CWE-94", "name": "Code Injection", "severity": "High"},
            {"cwe_id": "CWE-918", "name": "Server-Side Request Forgery", "severity": "High"}
        ]
        
        for vuln in vulnerabilities:
            result = conn.execute(text("SELECT id FROM vulnerabilities WHERE cwe_id = :cwe_id"), {"cwe_id": vuln["cwe_id"]})
            if not result.fetchone():
                conn.execute(
                    text("INSERT INTO vulnerabilities (cwe_id, name, severity) VALUES (:cwe_id, :name, :severity)"),
                    vuln
                )
                logger.info(f"Vulnerabilità '{vuln['cwe_id']}' creata")
        
        conn.commit()
        logger.info("Entità di riferimento create con successo")
        
        # 3. Importa i privacy patterns dal CSV
        logger.info(f"Importazione privacy patterns da {file_path}...")
        
        # Contatori
        patterns_created = 0
        patterns_skipped = 0
        
        # Prova diverse codifiche
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as csvfile:
                    # Prova a leggere la prima riga per verificare codifica
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
                        result = conn.execute(
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
                            "created_at": now,
                            "updated_at": now
                        }
                        
                        # Inserisci il pattern di base
                        insert_result = conn.execute(
                            text("""
                                INSERT INTO privacy_patterns 
                                (title, description, context, problem, solution, consequences, 
                                 strategy, mvc_component, created_at, updated_at)
                                VALUES 
                                (:title, :description, :context, :problem, :solution, :consequences,
                                 :strategy, :mvc_component, :created_at, :updated_at)
                                RETURNING id
                            """),
                            pattern_data
                        )
                        pattern_id = insert_result.fetchone()[0]
                        conn.commit()
                        logger.info(f"Pattern di base '{title}' creato con ID {pattern_id}")
                        
                        # Aggiungi le relazioni GDPR
                        try:
                            gdpr_text = clean_str(row.get('Article GDPR Compliance with the Pattern', ''))
                            gdpr_refs = split_values(gdpr_text)
                            
                            for ref in gdpr_refs:
                                # Estrai il numero dell'articolo (es. "Article 32" -> "32")
                                article_num = ref.replace("Article", "").strip()
                                if "�" in article_num:
                                    article_num = article_num.split("�")[0].strip()
                                
                                # Cerca l'articolo GDPR
                                gdpr_result = conn.execute(
                                    text("SELECT id FROM gdpr_articles WHERE number = :number"),
                                    {"number": article_num}
                                )
                                gdpr = gdpr_result.fetchone()
                                
                                if gdpr:
                                    # Inserisci la relazione
                                    conn.execute(
                                        text("INSERT INTO pattern_gdpr_association (pattern_id, gdpr_id) VALUES (:pattern_id, :gdpr_id)"),
                                        {"pattern_id": pattern_id, "gdpr_id": gdpr.id}
                                    )
                                    logger.info(f"  Aggiunto riferimento GDPR: Articolo {article_num}")
                                else:
                                    logger.warning(f"  Articolo GDPR '{article_num}' non trovato nel database")
                            conn.commit()
                        except Exception as e:
                            conn.rollback()
                            logger.warning(f"  Errore aggiungendo riferimenti GDPR: {str(e)}")
                        
                        # Aggiungi le relazioni PbD
                        try:
                            pbd_text = clean_str(row.get('Privacy By Design Principles', ''))
                            pbd_refs = split_values(pbd_text, delimiter=',')
                            
                            for ref in pbd_refs:
                                # Cerca il principio PbD
                                pbd_result = conn.execute(
                                    text("SELECT id FROM pbd_principles WHERE name = :name"),
                                    {"name": ref}
                                )
                                pbd = pbd_result.fetchone()
                                
                                if pbd:
                                    # Inserisci la relazione
                                    conn.execute(
                                        text("INSERT INTO pattern_pbd_association (pattern_id, pbd_id) VALUES (:pattern_id, :pbd_id)"),
                                        {"pattern_id": pattern_id, "pbd_id": pbd.id}
                                    )
                                    logger.info(f"  Aggiunto principio PbD: {ref}")
                                else:
                                    logger.warning(f"  Principio PbD '{ref}' non trovato nel database")
                            conn.commit()
                        except Exception as e:
                            conn.rollback()
                            logger.warning(f"  Errore aggiungendo principi PbD: {str(e)}")
                        
                        # Aggiungi le relazioni ISO
                        try:
                            iso_text = clean_str(row.get('ISO 9241-210 Phase', ''))
                            iso_refs = split_values(iso_text, delimiter=',')
                            
                            for ref in iso_refs:
                                # Cerca la fase ISO
                                iso_result = conn.execute(
                                    text("SELECT id FROM iso_phases WHERE name = :name"),
                                    {"name": ref}
                                )
                                iso = iso_result.fetchone()
                                
                                if iso:
                                    # Inserisci la relazione
                                    conn.execute(
                                        text("INSERT INTO pattern_iso_association (pattern_id, iso_id) VALUES (:pattern_id, :iso_id)"),
                                        {"pattern_id": pattern_id, "iso_id": iso.id}
                                    )
                                    logger.info(f"  Aggiunta fase ISO: {ref}")
                                else:
                                    logger.warning(f"  Fase ISO '{ref}' non trovata nel database")
                            conn.commit()
                        except Exception as e:
                            conn.rollback()
                            logger.warning(f"  Errore aggiungendo fasi ISO: {str(e)}")
                        
                        # Aggiungi le relazioni Vulnerabilità
                        try:
                            vuln_text = clean_str(row.get('CWE Top 25 Most Dangerous Software Weaknesses OWASP Categories Associated', ''))
                            vuln_refs = split_values(vuln_text, delimiter=',')
                            
                            for ref in vuln_refs:
                                # Estrai il codice CWE (es. "CWE-306: ..." -> "CWE-306")
                                cwe_code = ref.split(':')[0].strip() if ':' in ref else ref
                                
                                # Cerca la vulnerabilità
                                vuln_result = conn.execute(
                                    text("SELECT id FROM vulnerabilities WHERE cwe_id = :cwe_id"),
                                    {"cwe_id": cwe_code}
                                )
                                vuln = vuln_result.fetchone()
                                
                                if vuln:
                                    # Inserisci la relazione
                                    conn.execute(
                                        text("INSERT INTO pattern_vulnerability_association (pattern_id, vulnerability_id) VALUES (:pattern_id, :vulnerability_id)"),
                                        {"pattern_id": pattern_id, "vulnerability_id": vuln.id}
                                    )
                                    logger.info(f"  Aggiunta vulnerabilità: {cwe_code}")
                                else:
                                    logger.warning(f"  Vulnerabilità '{cwe_code}' non trovata nel database")
                            conn.commit()
                        except Exception as e:
                            conn.rollback()
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
        conn.rollback()
        logger.error(f"Errore generale: {str(e)}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Crea tabelle e importa privacy patterns da CSV")
    parser.add_argument("file_path", help="Percorso del file CSV")
    parser.add_argument("--delimiter", default=";", help="Separatore CSV (default: ';')")
    
    args = parser.parse_args()
    
    logger.info("Avvio creazione tabelle e importazione...")
    success = create_tables_and_import(args.file_path, args.delimiter)
    
    if success:
        logger.info("Creazione tabelle e importazione completata con successo!")
        sys.exit(0)
    else:
        logger.error("Creazione tabelle e importazione fallita.")
        sys.exit(1)

