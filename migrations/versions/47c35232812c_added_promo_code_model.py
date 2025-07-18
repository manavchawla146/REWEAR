"""added promo code model

Revision ID: 47c35232812c
Revises: 26642615a719
Create Date: 2025-06-02 13:03:28.064741

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '47c35232812c'
down_revision = '26642615a719'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('promo_codes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('code', sa.String(length=20), nullable=False),
    sa.Column('discount_type', sa.String(length=20), nullable=False),
    sa.Column('discount_value', sa.Float(), nullable=False),
    sa.Column('valid_from', sa.DateTime(), nullable=False),
    sa.Column('valid_until', sa.DateTime(), nullable=False),
    sa.Column('max_uses', sa.Integer(), nullable=True),
    sa.Column('uses', sa.Integer(), nullable=True),
    sa.Column('min_order_value', sa.Float(), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('code')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('promo_codes')
    # ### end Alembic commands ###
