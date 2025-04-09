"""Script per generare una migrazione unificata che risolve tutti i problemi di schema."""
import alembic.config
import sys
import os

def main():
    # Aggiungi la directory root al path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    
    # Configura alembic
    alembic_args = [
        '--raiseerr',
        'revision',
        '--autogenerate',
        '-m', "align_models_with_database"
    ]
    
    # Esegui comando alembic
    alembic.config.main(argv=alembic_args)

if __name__ == "__main__":
    main()