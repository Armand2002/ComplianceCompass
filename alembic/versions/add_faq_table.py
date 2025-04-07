# alembic/versions/add_faq_table.py
"""
Aggiunta tabella FAQ come alternativa al chatbot

Revision ID: add_faq_table
Revises: add_search_indices
Create Date: 2025-04-07
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_faq_table'
down_revision = 'add_search_indices'
branch_labels = None
depends_on = None

def upgrade():
    # Crea tabella FAQ
    op.create_table(
        'faqs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('question', sa.String(length=255), nullable=False),
        sa.Column('answer', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Indice per ricerca nelle FAQ
    op.create_index(
        'idx_faqs_question_trgm',
        'faqs',
        [sa.text('question gin_trgm_ops')],
        postgresql_using='gin'
    )
    
    op.create_index(
        'idx_faqs_answer_trgm',
        'faqs',
        [sa.text('answer gin_trgm_ops')],
        postgresql_using='gin'
    )
    
    op.create_index(
        'idx_faqs_category',
        'faqs',
        ['category']
    )
    
    op.create_index(
        'idx_faqs_priority',
        'faqs',
        ['priority']
    )
    
    # Inserimento dati iniziali
    op.execute("""
    INSERT INTO faqs (question, answer, category, priority)
    VALUES 
        ('Cos''è un Privacy Pattern?', 
         'Un Privacy Pattern è una soluzione riutilizzabile per problemi comuni di privacy nella progettazione di sistemi software. I pattern aiutano gli sviluppatori a incorporare best practice di privacy nel loro lavoro.',
         'generale', 1),
        
        ('Come posso cercare un Privacy Pattern?', 
         'Puoi utilizzare la barra di ricerca nella parte superiore della pagina. Inserisci parole chiave come ''consenso'', ''minimizzazione'' o ''pseudonimizzazione''. Puoi anche utilizzare i filtri per affinare la tua ricerca.',
         'utilizzo', 2),
        
        ('Cosa sono i principi Privacy by Design?', 
         'Privacy by Design (PbD) è un approccio che integra la privacy in tutto il ciclo di sviluppo. I suoi sette principi fondamentali includono: Proattività, Privacy come impostazione predefinita, Privacy incorporata nel design, Funzionalità completa, Sicurezza end-to-end, Visibilità/Trasparenza, e Rispetto per la privacy dell''utente.',
         'generale', 3),
         
        ('Come sono classificati i Privacy Pattern?', 
         'I Privacy Pattern sono classificati per: Strategia (Minimizzazione, Separazione, Astrazione, ecc.), Componente MVC (Model, View, Controller), Fase ISO 9241-210, Articoli GDPR correlati, e Principi Privacy by Design implementati.',
         'generale', 4),
         
        ('Cos''è il GDPR?', 
         'Il GDPR (General Data Protection Regulation) è un regolamento dell''Unione Europea sulla protezione dei dati e la privacy. Stabilisce regole per la raccolta, l''elaborazione e la conservazione dei dati personali, imponendo obblighi alle organizzazioni e garantendo diritti agli individui.',
         'normative', 5)
    """)

def downgrade():
    op.drop_index('idx_faqs_priority')
    op.drop_index('idx_faqs_category')
    op.drop_index('idx_faqs_answer_trgm')
    op.drop_index('idx_faqs_question_trgm')
    op.drop_table('faqs')