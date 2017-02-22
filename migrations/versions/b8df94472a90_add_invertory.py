"""add invertory

Revision ID: b8df94472a90
Revises: 1e3b94c19549
Create Date: 2017-02-22 15:45:52.011293

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b8df94472a90'
down_revision = '1e3b94c19549'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('inventories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('product_sku_id', sa.Integer(), nullable=True),
    sa.Column('type', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('user_name', sa.String(length=200), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('production_date', sa.Date(), nullable=True),
    sa.Column('valid_until', sa.Date(), nullable=True),
    sa.Column('batch_no', sa.String(length=30), nullable=True),
    sa.ForeignKeyConstraint(['product_sku_id'], ['product_skus.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('inventories')
    # ### end Alembic commands ###
