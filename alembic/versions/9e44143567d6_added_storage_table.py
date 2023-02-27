"""added storage table

Revision ID: 9e44143567d6
Revises: 386d51413d4c
Create Date: 2023-02-24 00:27:08.606687+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9e44143567d6'
down_revision = '386d51413d4c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('storage',
    sa.Column('mount_id', sa.Integer(), nullable=False),
    sa.Column('nfs_mnt', sa.String(length=255), nullable=False),
    sa.Column('local_mnt', sa.String(length=255), nullable=False),
    sa.Column('storage_cap', sa.BigInteger(), nullable=False),
    sa.Column('op_status', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('mount_id')
    )
    op.alter_column('hardware', 'mount_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.create_foreign_key(None, 'hardware', 'storage', ['mount_id'], ['mount_id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'hardware', type_='foreignkey')
    op.alter_column('hardware', 'mount_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.drop_table('storage')
    # ### end Alembic commands ###
