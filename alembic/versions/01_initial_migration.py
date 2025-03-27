"""Initial database migration

Revision ID: 01_initial_migration
Revises: 
Create Date: 2025-03-28 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import enum


# revision identifiers, used by Alembic.
revision = '01_initial_migration'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Creazione delle enum
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=100), nullable=True),
        sa.Column('role', sa.Enum('ADMIN', 'EDITOR', 'VIEWER', name='userrole'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('avatar_url', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    
    # Tabella gdpr_articles
    op.create_table('gdpr_articles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('number', sa.String(length=10), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('number')
    )
    op.create_index(op.f('ix_gdpr_articles_category'), 'gdpr_articles', ['category'], unique=False)
    op.create_index(op.f('ix_gdpr_articles_id'), 'gdpr_articles', ['id'], unique=False)
    op.create_index(op.f('ix_gdpr_articles_number'), 'gdpr_articles', ['number'], unique=True)
    
    # Tabella pbd_principles
    op.create_table('pbd_principles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('guidance', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_pbd_principles_id'), 'pbd_principles', ['id'], unique=False)
    op.create_index(op.f('ix_pbd_principles_name'), 'pbd_principles', ['name'], unique=True)
    
    # Tabella iso_phases
    op.create_table('iso_phases',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('standard', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('order', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_iso_phases_id'), 'iso_phases', ['id'], unique=False)
    op.create_index(op.f('ix_iso_phases_name'), 'iso_phases', ['name'], unique=True)
    
    # Tabella vulnerabilities
    op.create_table('vulnerabilities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('severity', sa.Enum('LOW', 'MEDIUM', 'HIGH', 'CRITICAL', name='severitylevel'), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('cwe_id', sa.String(length=20), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_vulnerabilities_category'), 'vulnerabilities', ['category'], unique=False)
    op.create_index(op.f('ix_vulnerabilities_id'), 'vulnerabilities', ['id'], unique=False)
    op.create_index(op.f('ix_vulnerabilities_name'), 'vulnerabilities', ['name'], unique=True)
    
    # Tabella privacy_patterns
    op.create_table('privacy_patterns',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('context', sa.Text(), nullable=False),
        sa.Column('problem', sa.Text(), nullable=False),
        sa.Column('solution', sa.Text(), nullable=False),
        sa.Column('consequences', sa.Text(), nullable=False),
        sa.Column('strategy', sa.String(length=100), nullable=False),
        sa.Column('mvc_component', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('created_by_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('title')
    )
    op.create_index(op.f('ix_privacy_patterns_id'), 'privacy_patterns', ['id'], unique=False)
    op.create_index(op.f('ix_privacy_patterns_mvc_component'), 'privacy_patterns', ['mvc_component'], unique=False)
    op.create_index(op.f('ix_privacy_patterns_strategy'), 'privacy_patterns', ['strategy'], unique=False)
    op.create_index(op.f('ix_privacy_patterns_title'), 'privacy_patterns', ['title'], unique=True)
    
    # Tabella implementation_examples
    op.create_table('implementation_examples',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('code', sa.Text(), nullable=True),
        sa.Column('language', sa.String(length=50), nullable=True),
        sa.Column('diagram_url', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('created_by_id', sa.Integer(), nullable=True),
        sa.Column('pattern_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['pattern_id'], ['privacy_patterns.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_implementation_examples_id'), 'implementation_examples', ['id'], unique=False)
    
    # Tabella notifications
    op.create_table('notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('type', sa.Enum('INFO', 'WARNING', 'ERROR', 'SUCCESS', 'UPDATE', name='notificationtype'), nullable=False),
        sa.Column('is_read', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('read_at', sa.DateTime(), nullable=True),
        sa.Column('related_object_id', sa.Integer(), nullable=True),
        sa.Column('related_object_type', sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notifications_id'), 'notifications', ['id'], unique=False)
    
    # Tabelle di associazione
    op.create_table('pattern_gdpr_association',
        sa.Column('pattern_id', sa.Integer(), nullable=True),
        sa.Column('gdpr_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['gdpr_id'], ['gdpr_articles.id'], ),
        sa.ForeignKeyConstraint(['pattern_id'], ['privacy_patterns.id'], )
    )
    
    op.create_table('pattern_pbd_association',
        sa.Column('pattern_id', sa.Integer(), nullable=True),
        sa.Column('pbd_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['pbd_id'], ['pbd_principles.id'], ),
        sa.ForeignKeyConstraint(['pattern_id'], ['privacy_patterns.id'], )
    )
    
    op.create_table('pattern_iso_association',
        sa.Column('pattern_id', sa.Integer(), nullable=True),
        sa.Column('iso_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['iso_id'], ['iso_phases.id'], ),
        sa.ForeignKeyConstraint(['pattern_id'], ['privacy_patterns.id'], )
    )
    
    op.create_table('pattern_vulnerability_association',
        sa.Column('pattern_id', sa.Integer(), nullable=True),
        sa.Column('vulnerability_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['pattern_id'], ['privacy_patterns.id'], ),
        sa.ForeignKeyConstraint(['vulnerability_id'], ['vulnerabilities.id'], )
    )


def downgrade():
    # Rimuovi prima le tabelle di associazione
    op.drop_table('pattern_vulnerability_association')
    op.drop_table('pattern_iso_association')
    op.drop_table('pattern_pbd_association')
    op.drop_table('pattern_gdpr_association')
    
    # Rimuovi le tabelle principali
    op.drop_table('notifications')
    op.drop_table('implementation_examples')
    op.drop_table('privacy_patterns')
    op.drop_table('vulnerabilities')
    op.drop_table('iso_phases')
    op.drop_table('pbd_principles')
    op.drop_table('gdpr_articles')
    op.drop_table('users')
    
    # Rimuovi enum
    op.execute("DROP TYPE userrole")
    op.execute("DROP TYPE severitylevel")
    op.execute("DROP TYPE notificationtype")