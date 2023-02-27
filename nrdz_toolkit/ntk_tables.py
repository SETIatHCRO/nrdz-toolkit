# -*- mode: python; coding: utf-8 -*-
# Copyright 2022 David R. DeBoer
# Licensed under the 2-clause BSD license.

"""All of the :tables defined here."""

from astropy.time import Time
from geoalchemy2 import Geometry
from sqlalchemy import (
        BigInteger, 
        Boolean, 
        CHAR, 
        Column, 
        DateTime, 
        Float, 
        ForeignKey, 
        ForeignKeyConstraint, 
        Integer, 
        Numeric, 
        String, 
        TIMESTAMP, 
        Text, 
        func
    )
from sqlalchemy.dialects.postgresql import INET, MACADDR
from sqlalchemy.orm import relationship
from . import CMDeclarativeBase, NotNull
import copy

class storage(CMDeclarativeBase):
    """
    Details on how the storage is organized.

    Attributes
    ----------
    mount_id : Integer Column
        Identifying parameter for where a file, file system or directory
        is made accessible on the server. Primary key.
    nfs_mnt : String Column
        Network File System mount. Allows hosts to mount file systems over
        a network and interact with those file systems as though they are 
        mounted locally.
    local_mnt : String Column
        Local mount. Connects disc drives on one machine so that they behave 
        as one logical system.
    storage_cap : BigInteger Column
        Amount of storage remaining on a mount.
    op_status : Boolean Column
        Operational status: 0 signifies "offline" while 1 signifies "online".
    """

    __tablename__ = "storage"

    mount_id = Column(Integer(), primary_key=True)
    nfs_mnt = Column(String(255), nullable=False)
    local_mnt = Column(String(255), nullable=False)
    storage_cap = Column(BigInteger(), nullable=False)
    op_status = Column(Boolean(), nullable=False)

    hardware = relationship("hardware")

class hardware(CMDeclarativeBase):
    """
    Fixed hardware parameters of HCRO-NRDZ sensors.

    Attributes
    ----------
    hardware_id : Integer Column
        Identification number for each sensor. Primary key
    location : Point Column
        Physical location of each sensor in lat/long coordinates.
    enclosure : Boolean Column
        Determines if the device is enclosed in the EMI box.
        0 signifies "not enclosed" while 1 signifies "enclosed".
    mount_id : Integer Column
        Identifying parameter for where a file, file system or directory
        is made accessible on the server. Foreign key from storage table.
    op_status : Boolean Column
        Operational status: 0 signifies "offline" while 1 signifies "online".
    """

    __tablename__ = "hardware"

    hardware_id = Column(Integer(), primary_key=True)
    location = Column(Geometry('POINT'), nullable=False)
    enclosure = Column(Boolean(), nullable=False)
    op_status = Column(Boolean(), nullable=False)
    mount_id = Column(Integer(), 
            ForeignKey('storage.mount_id'),
            nullable=False
        )
    recordings = relationship('recordings')
    rpi = relationship('rpi')
    sdr = relationship('sdr')
    wrlen = relationship('wrlen')
    status = relationship('status')

class metadata(CMDeclarativeBase):
    """
    Metadata from sensor observations.

    Attributes:
    -----------
    metadata_id : Integer Column
        Identification numbers for all metadata.
    org : String Column
        Differentiates between the organizations who collected data.
        Can be either HCRO or CU.
    frequency : BigInteger Column
        Center frequency at which the observation was made.
    sample_rate : BigInteger Column
        Number of samples per second that are taken of a waveform.
    bandwidth : BigInteger Column
        The range of frequencies sampled during an observation.
    gain : Integer Column
        Factor by which the waveform's amplitude has changed during processing.
    length : Numeric Column 
        Length of an I/Q data recording in seconds.
        Default length: 1 second.
    interval : Numeric Column
        Time between each recording of data in seconds.
        Default interval: 10 seconds.
    bit_depth : String Column
        How data is stored in bits.
        Default bit_depth: 16 bits.
    """

    __tablename__ = "metadata"

    metadata_id = Column(Integer(), primary_key=True)
    org = Column(String(100), nullable=False)
    frequency = Column(BigInteger(), nullable=False)
    sample_rate = Column(BigInteger(), nullable=False)
    gain = Column(Integer(), nullable=False)
    length = Column(Numeric(), nullable=False)
    interval = Column(Numeric(), nullable=False)
    bit_depth = Column(String(10), nullable=False)

    recordings = relationship('recordings')

class recordings(CMDeclarativeBase):
    """
    Outlines how the recorded I/Q data is organized for each observation.

    Attributes:
    -----------
    recording_id : BigInteger Column
        Identifying parameter of each recording.
    hardware_id : Integer Column
        Identifying parameter of the corresponding sensor that recorded data.
        Foreign key from hardware table.
    metadata_id : Integer Column
        Identifying parameter of the metadata from each observation.
        Foreign key from metadata table.
    file_name : String Column
        Name of the recordings file.
    file_path : String Column
        Where the recordings file is located in the directory.
    survey_id : String Column
        Identifying parameter of the observing group the recording was part of.
    created_at : Timestamp Column
        Timestamp at which recordings file was created.
    entered_at : Timestamp Column
        Timestamp at which recordings file was entered into the database.
    """

    __tablename__ = "recordings"

    recording_id = Column(BigInteger(), primary_key=True)
    hardware_id = Column(Integer(), 
            ForeignKey('hardware.hardware_id'),
            nullable=False
        )
    metadata_id = Column(Integer(), 
            ForeignKey('metadata.metadata_id'),
            nullable=False
        )
    file_name = Column(String(100), nullable=False)
    file_path = Column(String(255), nullable=False)
    survey_id = Column(CHAR(6), nullable=False)
    created_at = Column(TIMESTAMP(), nullable=False)
    entered_at = Column(TIMESTAMP(), nullable=False)

    outputs = relationship('outputs')

class outputs(CMDeclarativeBase):
    """
    Details on the outputs of our data.

    Attributes:
    -----------
    output_id : BigInteger Column
        Identifying parameter for the output of each set of data.
    recording_id : Integer Column
        Identifying output of the recording that corresonds to each output.
    average_db : Numeric Column
        Average level of noise output in a given recording in units of decibels.
        (21, 16).
    max_db : Numeric Column
        Maximum level of noise output in a given recording in units of decibels.
        (21, 16).
    median_db : Numeric Column
        Median level of noise in a given recording in units of decibels.
        (21, 16).
    std_dev : Numeric Column
        Standard deviation of noise in a given recording in units of decibels.
    kurtosis : Numeric Column
        A measure of the tailedness in a noise distribution of a given
        distribution in units of decibels.
    """

    __tablename__ = "outputs"

    output_id = Column(BigInteger(), primary_key=True)
    recording_id = Column(Integer(),
            ForeignKey('recordings.recording_id'),
            nullable=False
        )
    average_db = Column(Numeric(21, 16), nullable=False)
    max_db = Column(Numeric(21, 16), nullable=False)
    median_db = Column(Numeric(21, 16), nullable=False)
    std_dev = Column(Numeric(), nullable=False)
    kurtosis = Column(Numeric(), nullable=False)

class rpi(CMDeclarativeBase):
    """
    A table for fixed parameters of the Raspberry Pi's in the sensors.
    
    Attributes
    ----------
    rpi_id : Integer Column
        Identification for the Raspberry Pi's of each sensor. Primary key.
    hostname : String Column
        Label assigned to each Raspberry Pi connected to the server.
    rpi_ip : INET Column
        Raspberry Pi IP address.
    rpi_mac : MACADDR Column
        Raspberry Pi MAC address.
    rpi_v : String Column
        Raspberry Pi version. 
    os_v : String Column
        Operating Software version.
    memory : BigInteger Column
        Amount of information available for immediate use.
    storage_cap : BigInteger Column
        Amount of total storage available.
    cpu_type : String Column
        Type of cpu in use.
    cpu_cores : Integer Column
        Number of cores in the cpu.
    op_status : Boolean Column
        Operational status: 0 signifies "offline" while 1 signifies "online".
    hardware_id : Integer Column
        ID of the corresponding sensor. 
    """

    __tablename__ = "rpi"

    rpi_id = Column(Integer(), primary_key=True)
    hostname = Column(String(100), nullable=False)
    rpi_ip = Column(INET(), nullable=False)
    rpi_mac = Column(MACADDR(), nullable=False)
    rpi_v = Column(String(255), nullable=False)
    os_v = Column(String(255), nullable=False)
    memory = Column(BigInteger(), nullable=False)
    storage_cap = Column(BigInteger(), nullable=False)
    cpu_type = Column(String(255), nullable=False)
    cpu_cores = Column(Integer(), nullable=False)
    op_status = Column(Boolean(), nullable=False)
    hardware_id = Column(Integer(),
            ForeignKey('hardware.hardware_id'),
            nullable=False
        )

class sdr(CMDeclarativeBase):
    """
    Table for fixed parameters of the software defined radios in the sensors.
    
    Attributes:
    -----------
    sdr_id : Integer Column
        Identification parameter for the software defined radios in the sensors.    sdr_serial : String Column
        SDR serial number.
    mboard_name : String Column
        Name of the SDR's motherboard.
    external clock : Boolean Column
        Determines whether or not the SDR's are being overclocked.
    op_status : Boolean Column
        Operational status: 0 signifies "offline" while 1 signifies "online".
    hardware_id : Integer Column
        ID of the corresponding sensor.
    """

    __tablename__ = "sdr"

    sdr_id = Column(Integer(), primary_key=True)
    sdr_serial = Column(CHAR(), nullable=False)
    mboard_name = Column(String(255), nullable=False)
    external_clock = Column(Boolean(), nullable=False)
    op_status = Column(Boolean(), nullable=False)
    hardware_id = Column(Integer(),
            ForeignKey('hardware.hardware_id'),
            nullable=False
        )

class wrlen(CMDeclarativeBase):
    """
    Table for fixed White Rabbit parameters

    Attributes:
    -----------
    wr_id : Integer Column
        Identification for the White Rabbits of each sensor.
    wr_srial : String Column
        White Rabbit serial number.
    wr_host : String Column
        White Rabbit hostname.
    wr_ip : INET Column
        White Rabbit IP address.
    wr_mac : MACADDR Column
        White Rabbit MAC address.
    mode : String Column
        Operation mode of the WR PTP Core - <WR Master, WR Slave>.
    hardware_id : Integer Column
        Identification of corresponding sensor. Foreign key from hardware.
    """

    __tablename__ = "wrlen"

    wr_id = Column(Integer(), primary_key=True)
    wr_serial = Column(String(100), nullable=False)
    wr_host = Column(String(100), nullable=False)
    wr_ip = Column(INET(), nullable=False)
    wr_mac = Column(MACADDR(), nullable=False)
    mode = Column(String(100), nullable=False)
    hardware_id = Column(Integer(),
            ForeignKey('hardware.hardware_id'),
            nullable=False
        )

class status(CMDeclarativeBase):
    """
    Table for all of the non-static parameters in our sensor.

    Attributes:
    -----------
    status_id : Integer Column
        Identification of each status.
    hostname : String Column
        Label assigned to each RPI connected to the server.
    time : Timestamp Column 
        Timestamp at which the data was pulled from the sensors.
    rpi_cpu_temp : Numeric Column
        CPU temperature of the RPI.
    sdr_temp : Numeric Column
        Software Defiend Radio temperature.
    avg_cpu_usage : Numeric Column
        Average CPU usage.
    bytes_recorded : BigInteger Column
    rem_nfs_storage_cap : BigInteger Column
        Remaining storage on the server.
    rem_rpi_storage_cap : BigInteger Column
        Remaining storage on the RPI.
    rpi_uptime_minutes : BigInteger Column
        Amount of time RPI has been active in units of minutes.
    hardware_id : Integer Column
        Identification of the corresponding sensors from which the data was
        pulled. Foreign key from hardware.
    wr_servo_state : String Column
        Servo state - Current state of WR servo state machine 
        - <Uninitialized, SYNC_SEC, SYNC_NSEC, SYNC_PHASE, TRACK_PHASE>.
    wr_sfp1_link : Boolean Column
        Determines if there’s a link to the first small form-factor 
        pluggable port. 0 for "inactive", 1 for "active".
    wr_sfp2_link : Boolean Column
        Determines if there’s a link to the second small form-factor 
        pluggable port. 0 means "inactive", 1 means "active".
    wr_sfp1_tx : BigInteger Column
        Small form-factor pluggable tx counter #1.
    wr_sfp1_rx : BigInteger Column
        Small form-factor pluggable rx counter #1.
    wr_sfp2_tx : BigInteger Column
        Small form-factor pluggable tx counter #2.
    wr_sfp2_rx : BigInteger Column
        Small form-factor pluggable rx counter #2.
    wr_phase_setp : Integer Column
        Phase setpoint - Current Slave's clock phase shift value.
    wr_rtt : Integer Column
        Round-trip time delay. XXX need units
    wr_crtt : Integer Column
        Cable round-trip time delay - Round-trip fiber latency. XXX need units.
    wr_clck_offset : Boolean Column
        Clock offset - Slave to Master offset calculated by PTP daemon
        (offsetMS). 
    wr_updt_cnt : Integer Column
        Update counter - The value of a counter incremented every time the 
        WR servo is updated.
    wr_temp : Numeric Column
        System temperature of the WR.
    wr_host : String Column
        Name of the host that the WR is connected to.
    """

    __tablename__ = "status"

    status_id = Column(BigInteger(), primary_key=True)
    hostname = Column(String(50), nullable=False)
    time = Column(TIMESTAMP(), nullable=False)
    rpi_cpu_temp = Column(Numeric(), nullable=False)
    sdr_temp = Column(Numeric(), nullable=False)
    avg_cpu_usage = Column(Numeric(), nullable=False)
    bytes_recorded = Column(BigInteger(), nullable=False)
    rem_nfs_storage_cap = Column(BigInteger(), nullable=False)
    rem_rpi_storage_cap = Column(BigInteger(), nullable=False)
    rpi_uptime_minutes = Column(BigInteger(), nullable=False)
    hardware_id = Column(Integer(),
            ForeignKey('hardware.hardware_id'),
            nullable=False
        )
    wr_servo_state = Column(String(50), nullable=False)
    wr_sfp1_link = Column(Boolean(), nullable=False)
    wr_sfp2_link = Column(Boolean(), nullable=False)
    wr_sfp1_tx = Column(BigInteger(), nullable=False)
    wr_sfp1_rx = Column(BigInteger(), nullable=False)
    wr_sfp2_tx = Column(BigInteger(), nullable=False)
    wr_sfp2_rx = Column(BigInteger(), nullable=False)
    wr_phase_setp = Column(Integer(), nullable=False)
    wr_rtt = Column(Integer(), nullable=False)
    wr_crtt = Column(Integer(), nullable=False)
    wr_clck_offset = Column(Boolean(), nullable=False)
    wr_updt_cnt = Column(Integer(), nullable=False)
    wr_temp = Column(Numeric(), nullable=False)
    wr_host = Column(String(100), nullable=False)
