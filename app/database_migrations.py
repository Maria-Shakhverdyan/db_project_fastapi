from alembic import op
import sqlalchemy as sa

"""
Migration script to add new columns to 'books' and 'readers' tables, and to add indexes.

Revision ID: 001_add_columns
Revises: None
Create Date: YYYY-MM-DD
"""

revision = '001_add_columns'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """
    Add 'year_published' column to 'books' table and 'email' column to 'readers' table.
    """
    op.add_column('books', sa.Column('year_published', sa.Integer(), nullable=True))
    op.add_column('readers', sa.Column('email', sa.String(length=255), nullable=True))

def downgrade():
    """
    Remove 'year_published' column from 'books' table and 'email' column from 'readers' table.
    """
    op.drop_column('books', 'year_published')
    op.drop_column('readers', 'email')

"""
Migration script to add indexes to 'books' and 'readers' tables.

Revision ID: 002_add_indexes
Revises: 001_add_columns
Create Date: YYYY-MM-DD
"""

revision = '002_add_indexes'
down_revision = '001_add_columns'
branch_labels = None
depends_on = None

def upgrade():
    """
    Add index to 'author' column in 'books' table and 'email' column in 'readers' table.
    """
    op.create_index('ix_books_author', 'books', ['author'])
    op.create_index('ix_readers_email', 'readers', ['email'])

def downgrade():
    """
    Remove index from 'author' column in 'books' table and 'email' column in 'readers' table.
    """
    op.drop_index('ix_books_author', table_name='books')
    op.drop_index('ix_readers_email', table_name='readers')
