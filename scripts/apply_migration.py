"""Script per applicare le migrazioni in modo sicuro."""
import alembic.config
import sys
import os
import subprocess

def backup_database():
    """Crea un backup del database prima della migrazione."""
    result = subprocess.run(
        ["pg_dump", "-h", "db", "-U", "postgres", "-d", "compliance_compass", "-f", "/tmp/backup_before_migration.sql"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"Errore nel backup del database: {result.stderr}")
        return False
    return True

def main():
    # Aggiungi la directory root al path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    
    # Backup database
    if not backup_database():
        print("Impossibile procedere senza backup")
        return
        
    # Applica migrazioni
    alembic_args = [
        '--raiseerr',
        'upgrade', 
        'head'
    ]
    
    # Esegui comando alembic
    try:
        alembic.config.main(argv=alembic_args)
        print("Migrazione applicata con successo!")
    except Exception as e:
        print(f"Errore durante la migrazione: {str(e)}")
        print("Consultare il backup in /tmp/backup_before_migration.sql")

if __name__ == "__main__":
    main()