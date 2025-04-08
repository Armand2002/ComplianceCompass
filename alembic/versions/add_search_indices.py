# alembic/versions/add_search_indices.py
"""
Aggiunta indici per ottimizzare ricerche SQL (sostituzione Elasticsearch)

Revision ID: add_search_indices
Revises: 20250408_add_newsletter_tables
Create Date: 2025-04-08 01:15:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = 'add_search_indices'
down_revision = '20250408_add_newsletter_tables'
branch_labels = None
depends_on = None

def index_exists(index_name, table_name):
    """Check if an index exists."""
    conn = op.get_bind()
    query = text(
        "SELECT 1 FROM pg_indexes WHERE indexname = :indexname AND tablename = :tablename"
    )
    result = conn.execute(query, {"indexname": index_name, "tablename": table_name}).scalar()
    return bool(result)

def upgrade():
    # Non ricreiamo indici già creati dalla migrazione precedente
    # Gli indici creati in 20250407_optimize_indices.py sono:
    # - idx_privacy_patterns_strategy_mvc
    # - idx_pattern_gdpr_association_pattern_id
    # - idx_pattern_pbd_association_pattern_id
    # - idx_pattern_iso_association_pattern_id
    # - idx_pattern_vulnerability_association_pattern_id
    # - idx_implementation_examples_pattern_id
    # - idx_notifications_user_id_is_read
    # - idx_privacy_patterns_fulltext_search
    # - idx_privacy_patterns_updated_at
    
    # Aggiungi solo nuovi indici qui, se necessario
    if not index_exists("idx_users_email", "users"):
        op.create_index('idx_users_email', 'users', ['email'])
        
    # Altri nuovi indici...

def downgrade():
    # Rimuovi solo gli indici creati in questa migrazione
    if index_exists("idx_users_email", "users"):
        op.drop_index('idx_users_email', table_name='users')
    
    # Altri drop per indici creati qui...