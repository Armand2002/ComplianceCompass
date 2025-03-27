# alembic/env.py
import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Aggiungi la directory principale al path per importare i moduli
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import dei modelli per riconoscimento Alembic
from src.models.base import Base
from src.models.user_model import User
from src.models.privacy_pattern import PrivacyPattern
from src.models.gdpr_model import GDPRArticle
from src.models.pbd_principle import PbDPrinciple
from src.models.iso_phase import ISOPhase
from src.models.vulnerability import Vulnerability
from src.models.implementation_example import ImplementationExample
from src.models.notification import Notification

# Import della configurazione
from src.config import settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpreta la configuration file per la configurazione di Python logging.
fileConfig(config.config_file_name)

# Aggiungi qui l'oggetto MetaData target per le migrazioni
target_metadata = Base.metadata

# Sovrascrivi l'URL del database dalla configurazione
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    Configura il contesto e chiama i migration runner con una connessione "virtuale".
    In modalità offline, non esegue effettivamente la connessione.
    
    Utile per autogenerare migrazioni da eseguire in un secondo momento.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In questa modalità, crea un Engine e li associa al
    contexto Migration con una connessione iniziata.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            # Genera migrazioni automatiche più intelligenti
            # rilevando rinomini di tabelle e colonne
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()