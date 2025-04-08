"""
Add optimized indices for enhanced query performance.

Revision ID: 20250407_optimize_indices
Revises: 01_initial_migration
Create Date: 2025-04-07 12:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = '20250407_optimize_indices'
down_revision = '01_initial_migration'
branch_labels = None
depends_on = None

# Disabilita la transazione per questa migrazione
__transactional_ddl__ = False

def index_exists(index_name, table_name):
    """Check if an index exists."""
    conn = op.get_bind()
    query = text(
        "SELECT 1 FROM pg_indexes WHERE indexname = :indexname AND tablename = :tablename"
    )
    result = conn.execute(query, {"indexname": index_name, "tablename": table_name}).scalar()
    return bool(result)

def upgrade():
    # Creare l'estensione pg_trgm prima di usare gli indici
    op.execute('CREATE EXTENSION IF NOT EXISTS pg_trgm;')
    
    # Crea indici non-concurrently (possono stare all'interno della stessa transazione)
    if not index_exists("idx_privacy_patterns_fulltext_search", "privacy_patterns"):
        op.create_index(
            'idx_privacy_patterns_fulltext_search',
            'privacy_patterns',
            ['title', 'description'],
            postgresql_using='gin',
            postgresql_ops={
                'title': 'gin_trgm_ops',
                'description': 'gin_trgm_ops'
            }
        )
    
    if not index_exists("idx_privacy_patterns_updated_at", "privacy_patterns"):
        op.create_index(
            'idx_privacy_patterns_updated_at',
            'privacy_patterns',
            [sa.text('updated_at DESC')]
        )
    
    # Rimosso l'uso di CONCURRENTLY per tutti gli indici
    # È meglio avere indici che funzionano piuttosto che indici ottimizzati che falliscono
    
    if not index_exists("idx_privacy_patterns_strategy_mvc", "privacy_patterns"):
        op.create_index(
            'idx_privacy_patterns_strategy_mvc',
            'privacy_patterns',
            ['strategy', 'mvc_component']
        )
    
    if not index_exists("idx_pattern_gdpr_association_pattern_id", "pattern_gdpr_association"):
        op.create_index(
            'idx_pattern_gdpr_association_pattern_id',
            'pattern_gdpr_association',
            ['pattern_id']
        )
    
    if not index_exists("idx_pattern_pbd_association_pattern_id", "pattern_pbd_association"):
        op.create_index(
            'idx_pattern_pbd_association_pattern_id',
            'pattern_pbd_association',
            ['pattern_id']
        )
    
    if not index_exists("idx_pattern_iso_association_pattern_id", "pattern_iso_association"):
        op.create_index(
            'idx_pattern_iso_association_pattern_id',
            'pattern_iso_association',
            ['pattern_id']
        )
    
    if not index_exists("idx_pattern_vulnerability_association_pattern_id", "pattern_vulnerability_association"):
        op.create_index(
            'idx_pattern_vulnerability_association_pattern_id',
            'pattern_vulnerability_association',
            ['pattern_id']
        )
    
    if not index_exists("idx_implementation_examples_pattern_id", "implementation_examples"):
        op.create_index(
            'idx_implementation_examples_pattern_id',
            'implementation_examples',
            ['pattern_id']
        )
    
    if not index_exists("idx_notifications_user_id_is_read", "notifications"):
        op.create_index(
            'idx_notifications_user_id_is_read',
            'notifications',
            ['user_id', 'is_read']
        )

def downgrade():
    # La rimozione degli indici può essere eseguita normalmente
    if index_exists("idx_notifications_user_id_is_read", "notifications"):
        op.drop_index('idx_notifications_user_id_is_read', table_name='notifications')
    
    if index_exists("idx_implementation_examples_pattern_id", "implementation_examples"):
        op.drop_index('idx_implementation_examples_pattern_id', table_name='implementation_examples')
    
    if index_exists("idx_pattern_vulnerability_association_pattern_id", "pattern_vulnerability_association"):
        op.drop_index('idx_pattern_vulnerability_association_pattern_id', table_name='pattern_vulnerability_association')
    
    if index_exists("idx_pattern_iso_association_pattern_id", "pattern_iso_association"):
        op.drop_index('idx_pattern_iso_association_pattern_id', table_name='pattern_iso_association')
    
    if index_exists("idx_pattern_pbd_association_pattern_id", "pattern_pbd_association"):
        op.drop_index('idx_pattern_pbd_association_pattern_id', table_name='pattern_pbd_association')
    
    if index_exists("idx_pattern_gdpr_association_pattern_id", "pattern_gdpr_association"):
        op.drop_index('idx_pattern_gdpr_association_pattern_id', table_name='pattern_gdpr_association')
    
    if index_exists("idx_privacy_patterns_updated_at", "privacy_patterns"):
        op.drop_index('idx_privacy_patterns_updated_at', table_name='privacy_patterns')
    
    if index_exists("idx_privacy_patterns_fulltext_search", "privacy_patterns"):
        op.drop_index('idx_privacy_patterns_fulltext_search', table_name='privacy_patterns')
    
    if index_exists("idx_privacy_patterns_strategy_mvc", "privacy_patterns"):
        op.drop_index('idx_privacy_patterns_strategy_mvc', table_name='privacy_patterns')
    
    # Non rimuoviamo l'estensione perché potrebbe essere usata da altre parti
    # op.execute('DROP EXTENSION IF EXISTS pg_trgm;')