# alembic/versions/add_search_indices.py
"""
Aggiunta indici per ottimizzare ricerche SQL (sostituzione Elasticsearch)

Revision ID: add_search_indices
Revises: 20250408_add_newsletter_tables
Create Date: 2025-04-07
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_search_indices'
down_revision = '20250408_add_newsletter_tables'
branch_labels = None
depends_on = None

def upgrade():
    # Indici per la ricerca full-text su PostgreSQL
    op.create_index(
        'idx_privacy_patterns_title_trgm',
        'privacy_patterns',
        [sa.text('title gin_trgm_ops')],
        postgresql_using='gin'
    )
    
    op.create_index(
        'idx_privacy_patterns_description_trgm',
        'privacy_patterns',
        [sa.text('description gin_trgm_ops')],
        postgresql_using='gin'
    )
    
    # Indici per ricerca con filtri
    op.create_index(
        'idx_privacy_patterns_strategy_mvc',
        'privacy_patterns',
        ['strategy', 'mvc_component']
    )
    
    # Indici per migliorare join performance
    op.create_index(
        'idx_pattern_gdpr_join',
        'pattern_gdpr_association',
        ['pattern_id', 'gdpr_id']
    )
    
    op.create_index(
        'idx_pattern_pbd_join',
        'pattern_pbd_association',
        ['pattern_id', 'pbd_id']
    )
    
    op.create_index(
        'idx_pattern_iso_join',
        'pattern_iso_association',
        ['pattern_id', 'iso_id']
    )
    
    op.create_index(
        'idx_pattern_vulnerability_join',
        'pattern_vulnerability_association',
        ['pattern_id', 'vulnerability_id']
    )

def downgrade():
    # Rimozione indici in ordine inverso
    op.drop_index('idx_pattern_vulnerability_join')
    op.drop_index('idx_pattern_iso_join')
    op.drop_index('idx_pattern_pbd_join')
    op.drop_index('idx_pattern_gdpr_join')
    op.drop_index('idx_privacy_patterns_strategy_mvc')
    op.drop_index('idx_privacy_patterns_description_trgm')
    op.drop_index('idx_privacy_patterns_title_trgm')