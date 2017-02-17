"""initial migration

Revision ID: 7d10f98a4ff1
Revises: 
Create Date: 2017-02-17 13:10:33.476949

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7d10f98a4ff1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('product_categories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('products',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('product_category_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('code', sa.String(length=32), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('product_image_links', sa.JSON(), nullable=True),
    sa.Column('rating', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['product_category_id'], ['product_categories.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('code')
    )
    op.create_table('sku_features',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('product_category_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('sku_feature_type', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['product_category_id'], ['product_categories.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('product_skus',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=True),
    sa.Column('code', sa.String(length=32), nullable=True),
    sa.Column('price', sa.Float(), nullable=True),
    sa.Column('stocks', sa.Integer(), nullable=True),
    sa.Column('barcode', sa.String(), nullable=True),
    sa.Column('hscode', sa.String(), nullable=True),
    sa.Column('weight', sa.Float(), nullable=True),
    sa.Column('stocks_for_order', sa.Integer(), nullable=True),
    sa.Column('thumbnail', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('code')
    )
    op.create_table('sku_options',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('sku_feature_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.ForeignKeyConstraint(['sku_feature_id'], ['sku_features.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('products_and_skuoptions',
    sa.Column('product_id', sa.Integer(), nullable=True),
    sa.Column('sku_option_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
    sa.ForeignKeyConstraint(['sku_option_id'], ['sku_options.id'], )
    )
    op.create_table('products_sku_options',
    sa.Column('product_sku_id', sa.Integer(), nullable=True),
    sa.Column('sku_option_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['product_sku_id'], ['product_skus.id'], ),
    sa.ForeignKeyConstraint(['sku_option_id'], ['sku_options.id'], )
    )
    # ### end Alembic commands ###
    op.execute("create sequence product_code_id_seq start with 1 increment by 1 ")
    op.execute("create sequence sku_code_id_seq start with 1 increment by 1 ")


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('products_sku_options')
    op.drop_table('products_and_skuoptions')
    op.drop_table('sku_options')
    op.drop_table('product_skus')
    op.drop_table('sku_features')
    op.drop_table('products')
    op.drop_table('product_categories')
    # ### end Alembic commands ###
    op.execute(sa.schema.DropSequence(sa.Sequence("product_code_id_seq")))
    op.execute(sa.schema.DropSequence(sa.Sequence("sku_code_id_seq")))