"""Add Google OAuth fields to User model

Revision ID: 26642615a719
Revises: 524655e28c90
Create Date: [some timestamp]
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '26642615a719'
down_revision = '524655e28c90'
branch_labels = None
depends_on = None

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('google_id', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('profile_picture', sa.String(length=200), nullable=True))
        batch_op.alter_column('password_hash', nullable=True)
        batch_op.create_unique_constraint('uq_users_google_id', ['google_id'])
    # ### end Alembic commands ###

def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint('uq_users_google_id', type_='unique')
        batch_op.alter_column('password_hash', nullable=False)
        batch_op.drop_column('profile_picture')
        batch_op.drop_column('google_id')
    # ### end Alembic commands ###