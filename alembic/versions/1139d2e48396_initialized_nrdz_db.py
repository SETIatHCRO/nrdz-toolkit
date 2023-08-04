"""initialized nrdz db

Revision ID: 1139d2e48396
Revises: 
Create Date: 2023-02-22 22:46:23.371361+00:00

"""
from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry

# revision identifiers, used by Alembic.
revision = '1139d2e48396'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('hardware',
    sa.Column('hardware_id', sa.Integer(), nullable=False),
    sa.Column('location', Geometry(geometry_type='POINT', from_text='ST_GeomFromEWKT', name='geometry'), nullable=False),
    sa.Column('enclosure', sa.Boolean(), nullable=False),
    sa.Column('op_status', sa.Boolean(), nullable=False),
    sa.Column('mount_id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('hardware_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('hardware')
    # ### end Alembic commands ###