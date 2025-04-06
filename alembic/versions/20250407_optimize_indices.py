"""
Add optimized indices for enhanced query performance.

Revision ID: 20250407_optimize_indices
Revises: 01_initial_migration
Create Date: 2025-04-07 14:25:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250407_optimize_indices'
down_revision = '01_initial_migration'
branch_labels = None
depends_on = None

def upgrade():
    # Indici per ottimizzazione ricerche frequenti
    op.create_index(
        'idx_privacy_patterns_strategy_mvc',
        'privacy_patterns',
        ['strategy', 'mvc_component'],
        postgresql_concurrently=True
    )
    
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
    
    op.create_index(
        'idx_privacy_patterns_updated_at',
        'privacy_patterns',
        [sa.text('updated_at DESC')],
        postgresql_concurrently=True
    )
    
    op.create_index(
        'idx_pattern_gdpr_association_pattern_id',
        'pattern_gdpr_association',
        ['pattern_id'],
        postgresql_concurrently=True
    )
    
    op.create_index(
        'idx_pattern_pbd_association_pattern_id',
        'pattern_pbd_association',
        ['pattern_id'],
        postgresql_concurrently=True
    )
    
    op.create_index(
        'idx_pattern_iso_association_pattern_id',
        'pattern_iso_association',
        ['pattern_id'],
        postgresql_concurrently=True
    )
    
    op.create_index(
        'idx_pattern_vulnerability_association_pattern_id',
        'pattern_vulnerability_association',
        ['pattern_id'],
        postgresql_concurrently=True
    )
    
    op.create_index(
        'idx_implementation_examples_pattern_id',
        'implementation_examples',
        ['pattern_id'],
        postgresql_concurrently=True
    )
    
    op.create_index(
        'idx_notifications_user_id_is_read',
        'notifications',
        ['user_id', 'is_read'],
        postgresql_concurrently=True
    )

def downgrade():
    # Drop indices in reverse order
    op.drop_index('idx_notifications_user_id_is_read')
    op.drop_index('idx_implementation_examples_pattern_id')
    op.drop_index('idx_pattern_vulnerability_association_pattern_id')
    op.drop_index('idx_pattern_iso_association_pattern_id')
    op.drop_index('idx_pattern_pbd_association_pattern_id')
    op.drop_index('idx_pattern_gdpr_association_pattern_id')
    op.drop_index('idx_privacy_patterns_updated_at')
    op.drop_index('idx_privacy_patterns_fulltext_search')
    op.drop_index('idx_privacy_patterns_strategy_mvc')