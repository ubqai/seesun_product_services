"""add share_stocks to inventory

Revision ID: ab10aa8faac9
Revises: 168b57a7f3a2
Create Date: 2017-03-06 11:33:46.892965

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ab10aa8faac9'
down_revision = '168b57a7f3a2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('inventories', sa.Column('share_stocks', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('inventories', 'share_stocks')
    # ### end Alembic commands ###
