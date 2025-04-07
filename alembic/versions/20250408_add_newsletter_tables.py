# alembic/versions/20250408_add_newsletter_tables.py
"""add newsletter tables

Revision ID: 20250408_add_newsletter_tables
Revises: 20250407_optimize_indices
Create Date: 2025-04-07

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = '20250408_add_newsletter_tables'
down_revision = '20250407_optimize_indices'
branch_labels = None
depends_on = None


def upgrade():
    # Tabella di sottoscrizioni newsletter
    op.create_table(
        'newsletter_subscription',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    
    # Tabella di preferenze newsletter
    op.create_table(
        'newsletter_preference',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('subscription_id', sa.Integer(), nullable=False),
        sa.Column('topic', sa.String(length=50), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.ForeignKeyConstraint(['subscription_id'], ['newsletter_subscription.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('subscription_id', 'topic')
    )
    
    # Tabella per la cronologia degli invii
    op.create_table(
        'newsletter_send_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('subscription_id', sa.Integer(), nullable=False),
        sa.Column('subject', sa.String(length=255), nullable=False),
        sa.Column('content_id', sa.String(length=100), nullable=False),
        sa.Column('sent_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.ForeignKeyConstraint(['subscription_id'], ['newsletter_subscription.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Indici per migliorare le performance
    op.create_index('idx_newsletter_subscription_email', 'newsletter_subscription', ['email'])
    op.create_index('idx_newsletter_subscription_active', 'newsletter_subscription', ['active'])
    op.create_index('idx_newsletter_preference_topic', 'newsletter_preference', ['topic'])
    op.create_index('idx_newsletter_send_history_sent_at', 'newsletter_send_history', ['sent_at'])


def downgrade():
    op.drop_table('newsletter_send_history')
    op.drop_table('newsletter_preference')
    op.drop_table('newsletter_subscription')