"""initialized db

Revision ID: fe568344379b
Revises: 
Create Date: 2023-07-24 19:16:38.011293+00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'fe568344379b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('metadata',
    sa.Column('metadata_id', sa.Integer(), sa.Identity(always=True), nullable=False),
    sa.Column('frequency', sa.BigInteger(), nullable=False),
    sa.Column('sample_rate', sa.BigInteger(), nullable=False),
    sa.Column('bandwidth', sa.BigInteger(), nullable=False),
    sa.Column('gain', sa.Integer(), nullable=False),
    sa.Column('length', sa.Numeric(), nullable=False),
    sa.Column('interval', sa.Numeric(), nullable=False),
    sa.Column('bit_depth', sa.String(length=10), nullable=True),
    sa.PrimaryKeyConstraint('metadata_id'),
    sa.UniqueConstraint('frequency', 'sample_rate', 'bandwidth', 'gain', 'length', 'interval', 'bit_depth', name='metadata_unique_key')
    )
    op.create_table('storage',
    sa.Column('mount_id', sa.Integer(), sa.Identity(always=True), nullable=False),
    sa.Column('nfs_mnt', sa.String(length=255), nullable=False),
    sa.Column('local_mnt', sa.String(length=255), nullable=False),
    sa.Column('storage_cap', sa.BigInteger(), nullable=False),
    sa.Column('op_status', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('mount_id'),
    sa.UniqueConstraint('nfs_mnt')
    )
    op.create_table('hardware',
    sa.Column('hardware_id', sa.Integer(), sa.Identity(always=True), nullable=False),
    sa.Column('location', sa.String(length=100), nullable=False),
    sa.Column('enclosure', sa.Boolean(), nullable=False),
    sa.Column('op_status', sa.Integer(), nullable=False),
    sa.Column('mount_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['mount_id'], ['storage.mount_id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('hardware_id')
    )
    op.create_table('outputs',
    sa.Column('output_id', sa.BigInteger(), sa.Identity(always=True), nullable=False),
    sa.Column('hardware_id', sa.Integer(), nullable=False),
    sa.Column('metadata_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('average_db', sa.Numeric(precision=21, scale=16), nullable=False),
    sa.Column('max_db', sa.Numeric(precision=21, scale=16), nullable=False),
    sa.Column('median_db', sa.Numeric(precision=21, scale=16), nullable=False),
    sa.Column('std_dev', sa.Numeric(), nullable=False),
    sa.Column('kurtosis', sa.Numeric(), nullable=False),
    sa.ForeignKeyConstraint(['hardware_id'], ['hardware.hardware_id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['metadata_id'], ['metadata.metadata_id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('output_id')
    )
    op.create_table('rpi',
    sa.Column('rpi_id', sa.Integer(), sa.Identity(always=True), nullable=False),
    sa.Column('hostname', sa.String(length=100), nullable=False),
    sa.Column('rpi_ip', postgresql.INET(), nullable=False),
    sa.Column('rpi_mac', postgresql.MACADDR(), nullable=False),
    sa.Column('rpi_v', sa.String(length=255), nullable=False),
    sa.Column('os_v', sa.String(length=255), nullable=False),
    sa.Column('memory', sa.BigInteger(), nullable=False),
    sa.Column('storage_cap', sa.BigInteger(), nullable=False),
    sa.Column('cpu_type', sa.String(length=255), nullable=False),
    sa.Column('cpu_cores', sa.Integer(), nullable=False),
    sa.Column('op_status', sa.Integer(), nullable=False),
    sa.Column('hardware_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['hardware_id'], ['hardware.hardware_id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('rpi_id'),
    sa.UniqueConstraint('hostname')
    )
    op.create_table('sdr',
    sa.Column('sdr_id', sa.Integer(), sa.Identity(always=True), nullable=False),
    sa.Column('sdr_serial', sa.CHAR(length=7), nullable=False),
    sa.Column('mboard_name', sa.String(length=255), nullable=False),
    sa.Column('external_clock', sa.Boolean(), nullable=False),
    sa.Column('op_status', sa.Integer(), nullable=False),
    sa.Column('hardware_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['hardware_id'], ['hardware.hardware_id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('sdr_id'),
    sa.UniqueConstraint('sdr_serial')
    )
    op.create_table('status',
    sa.Column('status_id', sa.BigInteger(), sa.Identity(always=True), nullable=False),
    sa.Column('hostname', sa.String(length=100), nullable=False),
    sa.Column('time', sa.DateTime(timezone=True), nullable=True),
    sa.Column('rpi_cpu_temp', sa.Numeric(), nullable=False),
    sa.Column('sdr_temp', sa.Numeric(), nullable=False),
    sa.Column('avg_cpu_usage', sa.Numeric(), nullable=False),
    sa.Column('bytes_recorded', sa.BigInteger(), nullable=False),
    sa.Column('rem_nfs_storage_cap', sa.BigInteger(), nullable=False),
    sa.Column('rem_rpi_storage_cap', sa.BigInteger(), nullable=False),
    sa.Column('rpi_uptime_minutes', sa.BigInteger(), nullable=False),
    sa.Column('hardware_id', sa.Integer(), nullable=False),
    sa.Column('wr_servo_state', sa.String(length=50), nullable=True),
    sa.Column('wr_sfp1_link', sa.Boolean(), nullable=True),
    sa.Column('wr_sfp2_link', sa.Boolean(), nullable=True),
    sa.Column('wr_sfp1_tx', sa.BigInteger(), nullable=True),
    sa.Column('wr_sfp1_rx', sa.BigInteger(), nullable=True),
    sa.Column('wr_sfp2_tx', sa.BigInteger(), nullable=True),
    sa.Column('wr_sfp2_rx', sa.BigInteger(), nullable=True),
    sa.Column('wr_phase_setp', sa.Integer(), nullable=True),
    sa.Column('wr_rtt', sa.Integer(), nullable=True),
    sa.Column('wr_crtt', sa.Integer(), nullable=True),
    sa.Column('wr_clck_offset', sa.Integer(), nullable=True),
    sa.Column('wr_updt_cnt', sa.Integer(), nullable=True),
    sa.Column('wr_temp', sa.Numeric(), nullable=True),
    sa.Column('wr_host', sa.String(length=100), nullable=True),
    sa.ForeignKeyConstraint(['hardware_id'], ['hardware.hardware_id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('status_id')
    )
    op.create_table('wrlen',
    sa.Column('wr_id', sa.Integer(), sa.Identity(always=True), nullable=False),
    sa.Column('wr_serial', sa.String(length=100), nullable=True),
    sa.Column('wr_ip', postgresql.INET(), nullable=True),
    sa.Column('wr_mac', postgresql.MACADDR(), nullable=True),
    sa.Column('mode', sa.String(length=100), nullable=True),
    sa.Column('wr_host', sa.String(length=100), nullable=True),
    sa.Column('op_status', sa.Integer(), nullable=False),
    sa.Column('hardware_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['hardware_id'], ['hardware.hardware_id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('wr_id'),
    sa.UniqueConstraint('wr_serial')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('wrlen')
    op.drop_table('status')
    op.drop_table('sdr')
    op.drop_table('rpi')
    op.drop_table('outputs')
    op.drop_table('hardware')
    op.drop_table('storage')
    op.drop_table('metadata')
    # ### end Alembic commands ###
