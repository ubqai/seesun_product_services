"""add price to inventory

Revision ID: 0b617c76ea17
Revises: a590804c67b7
Create Date: 2017-03-27 13:55:54.399896

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0b617c76ea17'
down_revision = 'a590804c67b7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('inventories', sa.Column('price', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('inventories', 'price')
    # ### end Alembic commands ###
