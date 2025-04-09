"""
Script per verificare l'integrità del database e correggere eventuali problemi.
"""
import sys
import os
import traceback
from sqlalchemy import MetaData, inspect, text

# Aggiungi la directory root al sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.db.session import SessionLocal, engine
from src.models.gdpr_model import GDPRArticle
from src.models.privacy_pattern import PrivacyPattern

def check_table_exists(inspector, table_name):
    """Verifica se una tabella esiste."""
    return table_name in inspector.get_table_names()

def check_column_exists(inspector, table_name, column_name):
    """Verifica se una colonna esiste in una tabella."""
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def main():
    try:
        db = SessionLocal()
        inspector = inspect(engine)
        
        print("=== Verifica integrità database ===")
        
        # Verifica tabelle principali
        for table_name in ["gdpr_articles", "privacy_patterns", "users"]:
            exists = check_table_exists(inspector, table_name)
            print(f"Tabella {table_name}: {'OK' if exists else 'MANCANTE'}")
            
        # Verifica colonna view_count in privacy_patterns
        if check_table_exists(inspector, "privacy_patterns"):
            has_view_count = check_column_exists(inspector, "privacy_patterns", "view_count")
            print(f"Colonna view_count in privacy_patterns: {'OK' if has_view_count else 'MANCANTE'}")
            
            # Aggiungi colonna se mancante
            if not has_view_count:
                print("Aggiunta della colonna view_count...")
                db.execute(text("ALTER TABLE privacy_patterns ADD COLUMN view_count INTEGER DEFAULT 0"))
                db.commit()
                print("Colonna view_count aggiunta correttamente.")
        
        # Verifica record nelle tabelle principali
        gdpr_count = db.query(GDPRArticle).count()
        pattern_count = db.query(PrivacyPattern).count()
        
        print(f"Articoli GDPR nel database: {gdpr_count}")
        print(f"Privacy Patterns nel database: {pattern_count}")
        
        print("\n=== Verifica completata ===")
        
    except Exception as e:
        print(f"Errore durante la verifica: {str(e)}")
        traceback.print_exc()
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    main()