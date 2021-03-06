"""add memo to sku

Revision ID: fecc0b8fc106
Revises: 849981dd4bf5
Create Date: 2017-04-12 14:20:20.351167

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'fecc0b8fc106'
down_revision = '849981dd4bf5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('product_skus', sa.Column('memo', sa.String(length=256), nullable=True))
    op.add_column('product_skus', sa.Column('name', sa.String(length=256), nullable=True))
    op.alter_column('products', 'length',
               existing_type=postgresql.DOUBLE_PRECISION(precision=53),
               type_=sa.String(length=256),
               existing_nullable=True)
    op.alter_column('products', 'width',
               existing_type=postgresql.DOUBLE_PRECISION(precision=53),
               type_=sa.String(length=256),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('products', 'width',
               existing_type=sa.String(length=256),
               type_=postgresql.DOUBLE_PRECISION(precision=53),
               existing_nullable=True)
    op.alter_column('products', 'length',
               existing_type=sa.String(length=256),
               type_=postgresql.DOUBLE_PRECISION(precision=53),
               existing_nullable=True)
    op.drop_column('product_skus', 'name')
    op.drop_column('product_skus', 'memo')
    # ### end Alembic commands ###
