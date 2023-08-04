"""added wrlen table

Revision ID: ea48d8e63ac4
Revises: 4c8e327c0ffe
Create Date: 2023-02-27 19:19:09.350169+00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'ea48d8e63ac4'
down_revision = '4c8e327c0ffe'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('wrlen',
    sa.Column('wr_id', sa.Integer(), nullable=False),
    sa.Column('wr_serial', sa.String(length=100), nullable=False),
    sa.Column('wr_host', sa.String(length=100), nullable=False),
    sa.Column('wr_ip', postgresql.INET(), nullable=False),
    sa.Column('wr_mac', postgresql.MACADDR(), nullable=False),
    sa.Column('mode', sa.String(length=100), nullable=False),
    sa.Column('hardware_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['hardware_id'], ['hardware.hardware_id'], ),
    sa.PrimaryKeyConstraint('wr_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('wrlen')
    # ### end Alembic commands ###