"""Initial migration

Revision ID: 5e9cde915a3e
Revises: 1de4365ff5a7
Create Date: 2025-04-08 11:32:39.579727

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5e9cde915a3e'
down_revision = '1de4365ff5a7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('query_records', schema=None) as batch_op:
        batch_op.add_column(sa.Column('answer', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('query_records', schema=None) as batch_op:
        batch_op.drop_column('answer')

    # ### end Alembic commands ###
