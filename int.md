# Piano di sviluppo per l'importazione CSV in Compliance Compass

Ora che hai a disposizione il file CSV `paste-2.txt`, posso offrirti un piano di sviluppo più mirato e semplificato. Questo piano è focalizzato esclusivamente sull'implementazione dello script CLI per importare i dati CSV nel tuo sistema.

## Fase 1: Preparazione (1 giorno)

### 1.1 Analisi del file CSV
- Esaminare la struttura del file CSV (colonne: Pattern, Strategies, Description Pattern, ecc.)
- Verificare la corrispondenza tra le colonne del CSV e le entità del database
- Identificare eventuali trasformazioni necessarie per i dati

### 1.2 Verifica delle dipendenze
- Non sono necessarie dipendenze aggiuntive per il parsing CSV, poiché utilizzeremo il modulo standard `csv` di Python

### 1.3 Aggiornamento del database
- Verifica che le entità di riferimento (GDPR, PbD, vulnerabilità) siano già popolate nel database
- Se necessario, crea script per popolare queste entità

## Fase 2: Implementazione dello script (1-2 giorni)

### 2.1 Creazione dello script di importazione
```
scripts/
  import_privacy_patterns.py  # Nuovo file
```

Lo script avrà queste funzionalità:
- Lettura del file CSV con supporto per diversi delimitatori (';', ',')
- Mappatura delle colonne CSV ai campi del modello
- Trasformazione dei valori (es. splitting di liste separate da virgole)
- Creazione dei pattern e delle loro relazioni
- Gestione degli errori e logging dettagliato
- Supporto per modalità "dry run" (simulazione senza modifiche al database)

### 2.2 Adattamenti specifici per il file CSV
- Gestione delle colonne con più valori (es. GDPR, PbD, OWASP)
- Pulizia dei dati (es. rimozione spazi, caratteri non validi)
- Mapping dei valori (es. "Model" → "Model", "View" → "View", "Controller" → "Controller")

## Fase 3: Testing e ottimizzazione (1 giorno)

### 3.1 Test manuali
- Test con un sottoinsieme del file CSV
- Verifica della corretta importazione e delle relazioni
- Verifica della gestione degli errori

### 3.2 Ottimizzazioni
- Miglioramento delle performance per file grandi
- Aggiunta di opzioni per la gestione dei duplicati
- Implementazione di transazioni atomiche

## Fase 4: Documentazione e finalizzazione (0.5 giorni)

### 4.1 Documentazione dello script
- Aggiungere commenti dettagliati e docstrings
- Creare una documentazione d'uso con esempi
- Aggiungere informazioni al README del progetto

### 4.2 Creazione di script di supporto
- Script per verificare lo stato dell'importazione
- Script per generare report sui dati importati

## Implementazione dello script

Ecco l'implementazione dello script di importazione basato sul tuo file CSV:

```python
#!/usr/bin/env python
"""
Script per importare privacy patterns da un file CSV nel database.

Uso:
    python -m scripts.import_privacy_patterns path/to/file.csv [--delimiter=";"] [--admin-id=1] [--dry-run]

Argomenti:
    file_path: Percorso del file CSV da importare
    --delimiter: Separatore CSV (default: ';')
    --admin-id: ID dell'utente admin (default: 1)
    --dry-run: Simula l'importazione senza modificare il database
"""
import os
import sys
import csv
import logging
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

# Aggiungi la directory principale al path per importare i moduli
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.privacy_pattern import PrivacyPattern
from src.models.gdpr_model import GDPRArticle
from src.models.pbd_principle import PbDPrinciple
from src.models.iso_phase import ISOPhase
from src.models.vulnerability import Vulnerability, SeverityLevel
from src.models.user_model import User
from src.db.session import SessionLocal

# Configurazione logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Mapping delle colonne CSV ai campi del modello
CSV_TO_MODEL_MAPPING = {
    "Pattern": "title",
    "Strategies": "strategy",
    "Description Pattern": "description",
    "Context Pattern": "context",
    "Collocazione MVC": "mvc_component",
    "ISO 9241-210 Phase": None,  # Gestito separatamente
    "Article GDPR Compliance with the Pattern": None,  # Gestito separatamente
    "Privacy By Design Principles": None,  # Gestito separatamente
    "OWASP Top Ten Categories": None,  # Gestito separatamente
    "CWE Top 25 Most Dangerous Software Weaknesses OWASP Categories Associated": None,  # Gestito separatamente
    "Examples": "consequences"  # Usiamo il campo examples come consequences per ora
}

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

def import_csv_data(file_path, admin_id=1, delimiter=';', dry_run=False):
    """
    Importa i dati dal file CSV nel database.
    
    Args:
        file_path: Percorso del file CSV
        admin_id: ID dell'utente admin che sarà impostato come creatore
        delimiter: Separatore utilizzato nel CSV
        dry_run: Se True, simula l'importazione senza modificare il database
    """
    db = SessionLocal()
    
    try:
        # Verifica che l'utente admin esista
        admin = db.query(User).filter(User.id == admin_id).first()
        if not admin:
            logger.error(f"Utente admin con ID {admin_id} non trovato!")
            return False
        
        logger.info(f"Admin trovato: {admin.username}")
        
        # Leggi il file CSV
        logger.info(f"Lettura del file {file_path}...")
        
        # Contatori
        patterns_created = 0
        patterns_skipped = 0
        
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            # Leggi l'intestazione per determinare i nomi delle colonne
            reader = csv.DictReader(csvfile, delimiter=delimiter)
            
            # Mostra le colonne trovate
            logger.info(f"Colonne trovate: {', '.join(reader.fieldnames)}")
            
            # Cicla ogni riga del file
            for row_index, row in enumerate(reader, start=2):  # Start=2 perché la prima riga è l'intestazione
                try:
                    # Estrai informazioni di base dal pattern
                    pattern_id = clean_str(row.get('#', '') or row.get('ID', ''))
                    title = clean_str(row.get('Pattern', ''))
                    
                    if not title:
                        logger.warning(f"Riga {row_index}: Titolo mancante, salto questa riga")
                        patterns_skipped += 1
                        continue
                    
                    # Log per debug
                    logger.info(f"Elaborazione pattern: {title} (ID: {pattern_id})")
                    
                    # Verifica se il pattern esiste già
                    if not dry_run:
                        existing_pattern = db.query(PrivacyPattern).filter(PrivacyPattern.title == title).first()
                        if existing_pattern:
                            logger.warning(f"Pattern '{title}' già esistente, salto")
                            patterns_skipped += 1
                            continue
                    
                    # Crea dizionario con i dati del pattern
                    pattern_data = {}
                    
                    # Mappatura campi base
                    for csv_field, model_field in CSV_TO_MODEL_MAPPING.items():
                        if model_field and csv_field in row:
                            pattern_data[model_field] = clean_str(row.get(csv_field, ''))
                    
                    # Campi mancanti nel mapping
                    pattern_data["problem"] = "Extracted from description"  # Valore predefinito
                    pattern_data["solution"] = "See examples for solutions"  # Valore predefinito
                    
                    # In modalità dry run, mostra solo i dati che verrebbero inseriti
                    if dry_run:
                        logger.info(f"DRY RUN - Pattern da creare: {pattern_data}")
                        patterns_created += 1
                        continue
                    
                    # Crea nuovo pattern
                    pattern = PrivacyPattern(
                        **pattern_data,
                        created_by_id=admin_id,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    
                    # Aggiungi relazioni se presenti
                    
                    # GDPR Articles
                    gdpr_text = clean_str(row.get('Article GDPR Compliance with the Pattern', ''))
                    gdpr_refs = split_values(gdpr_text)
                    for ref in gdpr_refs:
                        # Estrai il numero dell'articolo (es. "Article 32" -> "32")
                        article_num = ref.replace("Article", "").strip()
                        if "�" in article_num:
                            article_num = article_num.split("�")[0].strip()
                        
                        gdpr = db.query(GDPRArticle).filter(GDPRArticle.number == article_num).first()
                        if gdpr:
                            pattern.gdpr_articles.append(gdpr)
                            logger.info(f"  Aggiunto riferimento GDPR: Articolo {article_num}")
                        else:
                            logger.warning(f"  Articolo GDPR '{article_num}' non trovato nel database")
                    
                    # Privacy by Design
                    pbd_text = clean_str(row.get('Privacy By Design Principles', ''))
                    pbd_refs = split_values(pbd_text, delimiter=',')
                    for ref in pbd_refs:
                        pbd = db.query(PbDPrinciple).filter(PbDPrinciple.name == ref).first()
                        if pbd:
                            pattern.pbd_principles.append(pbd)
                            logger.info(f"  Aggiunto principio PbD: {ref}")
                        else:
                            logger.warning(f"  Principio PbD '{ref}' non trovato nel database")
                    
                    # ISO Phases
                    iso_text = clean_str(row.get('ISO 9241-210 Phase', ''))
                    iso_refs = split_values(iso_text, delimiter=',')
                    for ref in iso_refs:
                        iso = db.query(ISOPhase).filter(ISOPhase.name == ref).first()
                        if iso:
                            pattern.iso_phases.append(iso)
                            logger.info(f"  Aggiunta fase ISO: {ref}")
                        else:
                            logger.warning(f"  Fase ISO '{ref}' non trovata nel database")
                    
                    # Vulnerabilità (CWE)
                    vuln_text = clean_str(row.get('CWE Top 25 Most Dangerous Software Weaknesses OWASP Categories Associated', ''))
                    vuln_refs = split_values(vuln_text, delimiter=',')
                    for ref in vuln_refs:
                        # Estrai il codice CWE (es. "CWE-306: ..." -> "CWE-306")
                        cwe_code = ref.split(':')[0].strip() if ':' in ref else ref
                        
                        vuln = db.query(Vulnerability).filter(Vulnerability.cwe_id == cwe_code).first()
                        if vuln:
                            pattern.vulnerabilities.append(vuln)
                            logger.info(f"  Aggiunta vulnerabilità: {cwe_code}")
                        else:
                            logger.warning(f"  Vulnerabilità '{cwe_code}' non trovata nel database")
                    
                    # Salva nel database
                    db.add(pattern)
                    db.commit()
                    
                    patterns_created += 1
                    logger.info(f"Pattern '{title}' importato con successo")
                    
                except IntegrityError as e:
                    db.rollback()
                    logger.error(f"Errore di integrità alla riga {row_index}: {str(e)}")
                    patterns_skipped += 1
                except Exception as e:
                    db.rollback()
                    logger.error(f"Errore alla riga {row_index}: {str(e)}")
                    patterns_skipped += 1
        
        logger.info(f"Importazione completata. Patterns creati: {patterns_created}, saltati: {patterns_skipped}")
        return True
    
    except Exception as e:
        logger.error(f"Errore durante l'importazione: {str(e)}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Importa privacy patterns da CSV al database")
    parser.add_argument("file_path", help="Percorso del file CSV da importare")
    parser.add_argument("--admin-id", type=int, default=1, help="ID dell'utente admin (default: 1)")
    parser.add_argument("--delimiter", default=";", help="Separatore CSV (default: ';')")
    parser.add_argument("--dry-run", action="store_true", help="Simula l'importazione senza modificare il database")
    
    args = parser.parse_args()
    
    logger.info("Avvio importazione...")
    
    if args.dry_run:
        logger.info("MODALITÀ DRY RUN: nessuna modifica sarà apportata al database")
    
    success = import_csv_data(
        args.file_path, 
        admin_id=args.admin_id, 
        delimiter=args.delimiter,
        dry_run=args.dry_run
    )
    
    if success:
        logger.info("Importazione completata con successo!")
        sys.exit(0)
    else:
        logger.error("Importazione fallita.")
        sys.exit(1)
```

## Timeline e piano di lavoro

**Giorno 1:**
- Mattina: Analisi del file CSV e adattamento dello script
- Pomeriggio: Implementazione dello script di importazione

**Giorno 2:**
- Mattina: Testing dello script con un sottoinsieme di dati
- Pomeriggio: Ottimizzazione e correzione di eventuali problemi

**Giorno 3:**
- Mattina: Test completo dell'importazione
- Pomeriggio: Documentazione e finalizzazione

## Esecuzione

Per eseguire lo script di importazione:

```bash
# Copia il file CSV nel container
docker cp paste-2.txt compliance-compass-api:/app/privacy_patterns.csv

# Esegui lo script in modalità dry-run (simulazione)
docker-compose exec api python -m scripts.import_privacy_patterns privacy_patterns.csv --dry-run

# Esegui l'importazione effettiva
docker-compose exec api python -m scripts.import_privacy_patterns privacy_patterns.csv
```

Questo approccio è ideale per il tuo caso d'uso:
1. Utilizza solo librerie standard Python
2. Si concentra esclusivamente sulla funzionalità essenziale (CLI)
3. È facilmente adattabile al formato del tuo CSV
4. Implementa logging robusto e gestione degli errori
5. Richiede meno di 3 giorni per l'implementazione completa

Con questo piano, potrai facilmente importare i tuoi privacy patterns nel sistema Compliance Compass e concentrarti sugli aspetti di progettazione per il tuo esame universitario.