"""Initial migration

Revision ID: e8ca2a77bb4e
Revises: 45438ca9e5c2
Create Date: 2025-03-27 17:06:08.690285

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'e8ca2a77bb4e'
down_revision = '45438ca9e5c2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('branches', schema=None) as batch_op:
        batch_op.add_column(sa.Column('address', sa.String(length=255), nullable=False))
        batch_op.drop_column('description')
        batch_op.drop_column('name')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('branches', schema=None) as batch_op:
        batch_op.add_column(sa.Column('name', mysql.VARCHAR(length=255), nullable=False))
        batch_op.add_column(sa.Column('description', mysql.VARCHAR(length=1000), nullable=True))
        batch_op.drop_column('address')

    # ### end Alembic commands ###
