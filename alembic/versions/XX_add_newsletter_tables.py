# alembic/versions/XX_add_newsletter_tables.py
"""add newsletter tables

Revision ID: XX
Revises: [precedente revision ID]
Create Date: [data attuale]

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'XX'
down_revision = '[precedente revision ID]'
branch_labels = None
depends_on = None


def upgrade():
    # Tabella newsletter_subscriptions
    op.create_table('newsletter_subscriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('verification_token', sa.String(length=100), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=False, default=False),
        sa.Column('subscribed_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('last_updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_newsletter_subscriptions_id'), 'newsletter_subscriptions', ['id'], unique=False)
    op.create_index(op.f('ix_newsletter_subscriptions_email'), 'newsletter_subscriptions', ['email'], unique=True)
    
    # Tabella newsletter_issues
    op.create_table('newsletter_issues',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('subject', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('created_by_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_newsletter_issues_id'), 'newsletter_issues', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_newsletter_issues_id'), table_name='newsletter_issues')
    op.drop_table('newsletter_issues')
    op.drop_index(op.f('ix_newsletter_subscriptions_email'), table_name='newsletter_subscriptions')
    op.drop_index(op.f('ix_newsletter_subscriptions_id'), table_name='newsletter_subscriptions')
    op.drop_table('newsletter_subscriptions')