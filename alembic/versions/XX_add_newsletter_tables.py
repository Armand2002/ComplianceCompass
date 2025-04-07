# alembic/versions/XX_add_newsletter_tables.py
"""add newsletter tables

Revision ID: XX_add_newsletter_tables
Revises: 20250407_optimize_indices
Create Date: 2025-04-07 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid


# revision identifiers, used by Alembic.
revision = 'XX_add_newsletter_tables'
down_revision = '20250407_optimize_indices'
branch_labels = None
depends_on = None


def upgrade():
    # Tabella per gli abbonati alla newsletter
    op.create_table(
        'newsletter_subscribers',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('email', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('first_name', sa.String(100), nullable=True),
        sa.Column('last_name', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('confirmation_token', sa.String(255), nullable=True, unique=True),
        sa.Column('is_confirmed', sa.Boolean(), nullable=False, default=False),
        sa.Column('preferences', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    )
    
    # Indice per ottimizzare le ricerche per email
    op.create_index('idx_subscriber_email', 'newsletter_subscribers', ['email'])
    
    # Indice per le query di stato e conferma
    op.create_index('idx_subscriber_status', 'newsletter_subscribers', ['is_active', 'is_confirmed'])
    
    # Tabella per le newsletter inviate
    op.create_table(
        'newsletter_campaigns',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('subject', sa.String(255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('content_html', sa.Text(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, default='draft'),  # draft, scheduled, sent, cancelled
        sa.Column('scheduled_at', sa.DateTime(), nullable=True),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('target_segment', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    )
    
    # Indice per ottimizzare le query sullo stato delle campagne
    op.create_index('idx_campaign_status', 'newsletter_campaigns', ['status'])
    
    # Indice per le query di campagne programmate
    op.create_index('idx_campaign_scheduled', 'newsletter_campaigns', ['scheduled_at'])
    
    # Tabella per tracciare l'invio delle newsletter
    op.create_table(
        'newsletter_deliveries',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('campaign_id', UUID(as_uuid=True), sa.ForeignKey('newsletter_campaigns.id', ondelete='CASCADE'), nullable=False),
        sa.Column('subscriber_id', UUID(as_uuid=True), sa.ForeignKey('newsletter_subscribers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, default='pending'),  # pending, sent, delivered, opened, clicked, bounced, failed
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('delivered_at', sa.DateTime(), nullable=True),
        sa.Column('opened_at', sa.DateTime(), nullable=True),
        sa.Column('clicked_at', sa.DateTime(), nullable=True),
        sa.Column('error', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    )
    
    # Indice composito per ottimizzare le query di tracciamento
    op.create_index('idx_delivery_campaign_subscriber', 'newsletter_deliveries', ['campaign_id', 'subscriber_id'])
    
    # Indice per le query di stato delle consegne
    op.create_index('idx_delivery_status', 'newsletter_deliveries', ['status'])


def downgrade():
    op.drop_table('newsletter_deliveries')
    op.drop_table('newsletter_campaigns')
    op.drop_table('newsletter_subscribers')