# -*- mode: python; coding: utf-8 -*-
# Copyright 2022 David R. DeBoer
# Licensed under the 2-clause BSD license.

"""All of the :tables defined here."""

from astropy.time import Time
from sqlalchemy import (
        BigInteger, 
        Boolean,
        CHAR,
        Column, 
        DateTime, 
        Float, 
        ForeignKey, 
        Identity, 
        Integer, 
        Numeric, 
        String, 
        Text, 
        func, 
        UniqueConstraint
    )
from sqlalchemy.dialects.postgresql import INET, MACADDR
from geoalchemy2 import Geometry
from . import CMDeclarativeBase, NotNull
import copy

class status_codes(CMDeclarativeBase):
    """
    XXX DESCRIPTION NEEDED
    """

    __tablename__ = "status_codes"
    
    code_id = Column(Integer(), nullable=False, primary_key=True)
    description = Column(Text(), nullable=False)

class storage(CMDeclarativeBase):
    """
    XXX DESCRIPTION NEEDED
    """

    __tablename__ = "storage"

    mount_id = Column(Integer(), Identity(always=True), primary_key=True)
    nfs_mnt = Column(String(255), nullable=False, unique=True)
    local_mnt = Column(String(255), nullable=False)
    storage_cap = Column(BigInteger(), nullable=False)
    op_status = Column(
            Integer(), 
            ForeignKey(
                "status_codes.code_id", 
                onupdate="CASCADE", 
                ondelete="CASCADE"
            ), 
            nullable=False
        )

class hardware(CMDeclarativeBase):
    """
    A table that logs the fixed hardware parameters of the HCRO-NRDZ sensors.

    Attributes
    ----------
    hardware_id : String Column
        Identification for each sensor. The id is of notation 'hns-XXX'
        where hns = Hcro-Nrdz Sensor. Primary key
    loc : String Column
        Physical location of each sensor at HCRO.
    hostname : String Column
        DNS hostname.
    nfs_mnt : String Column
        Network File System mount.
    rpi_mac : String Column
        Raspberry Pi mac address.
    wr_mac : String Column
        White Rabbit mac address.
    rpi_ip : String Column
        Raspberry pi IP address.
    wr_ip : String Column
        White Rabbit IP address.
    usrp_sn : String Column
        USRP serial number.

    """

    __tablename__ = "hardware"

    hardware_id = Column(Integer(), Identity(always=True), primary_key=True)
    location = Column(Geometry('POINT'), nullable=False)
    enclosure = Column(Boolean(), nullable=False)
    op_status = Column(
            Integer(),
            ForeignKey(
                "status_codes.code_id",
                onupdate="CASCADE",
                ondelete="CASCADE"
            ),
            nullable=False
        )
    mount_id = Column(
            Integer(), 
            ForeignKey(
                "storage.mount_id",
                onupdate="CASCADE",
                ondelete="CASCADE"
            ), 
            nullable=False
        )

class status(CMDeclarativeBase):
    """
    Table that shows the current status of the unfixed sensor parameters.

    Attributes:
    -----------
    status_id : String Column
        Identification for each sensor. The id is of notation 'hns-XXX'
        where hns = Hcro-Nrdz Sensor. Primary key.
    time : Integer Column
        Timestamp in unix time at which the information was collected.
        Primary key.
    rpi_cpu_temp : Float Column
        Raspberry Pi CPU temperature.
    cpu_usage : Float Column
        RPI CPU usage at time of capture.
    avg_cpu_usage : Float Column
        Average CPU usage over time.
    bytes_recorded : BigInteger Column
        Number of bytes recorded. Unsure if this is for a single capture or 
        over the course of an observation. FOLLOWUP NEEDED
    storage_cap : Float Column
        Remaining storage on raspberry pi.
    hardware_id : String Column
        Foreign key from hardware table.
    
    """
       
    __tablename__ = "status"

    status_id = Column(BigInteger(), Identity(always=True), primary_key=True)
    hostname = Column(String(100), nullable=False)
    time = Column(DateTime(timezone=True), primary_key=True)
    rpi_cpu_temp = Column(Numeric(), nullable=False)
    sdr_temp = Column(Numeric(), nullable=False)
    avg_cpu_usage = Column(Numeric(), nullable=False)
    bytes_recorded = Column(BigInteger(), nullable=False)
    rem_nfs_storage_cap = Column(BigInteger(), nullable=False)
    rem_rpi_storage_cap = Column(BigInteger(), nullable=False)
    rpi_uptime_minutes = Column(BigInteger(), nullable=False)
    hardware_id = Column(
            Integer(), 
            ForeignKey(
                "hardware.hardware_id",
                onupdate="CASCADE",
                ondelete="CASCADE",
            ),
            nullable=False
        )
    wr_servo_state = Column(String(50), nullable=True)
    wr_sfp1_link = Column(Boolean(), nullable=True)
    wr_sfp2_link = Column(Boolean(), nullable=True)
    wr_sfp1_tx = Column(BigInteger(), nullable=True)
    wr_sfp1_rx = Column(BigInteger(), nullable=True)
    wr_sfp2_tx = Column(BigInteger(), nullable=True)
    wr_sfp2_rx = Column(BigInteger(), nullable=True)
    wr_phase_setp = Column(Integer(), nullable=True)
    wr_rtt = Column(Integer(), nullable=True)
    wr_crtt = Column(Integer(), nullable=True)
    wr_clck_offset = Column(Integer(), nullable=True)
    wr_updt_cnt = Column(Integer(), nullable=True)
    wr_temp = Column(Numeric(), nullable=True)
    wr_host = Column(String(100), nullable=True)

class rpi(CMDeclarativeBase):
    """
    XXX DESCRIPTION NEEDED
    """

    __tablename__ = "rpi"

    rpi_id = Column(Integer(), Identity(always=True), primary_key=True)
    hostname = Column(String(100), nullable=False, unique=True)
    rpi_ip = Column(INET(), nullable=False)
    rpi_mac = Column(MACADDR(), nullable=False)
    rpi_v = Column(String(255), nullable=False)
    os_v = Column(String(255), nullable=False)
    memory = Column(BigInteger(), nullable=False)
    storage_cap = Column(BigInteger(), nullable=False)
    cpu_type = Column(Integer(), nullable=False)
    cpu_cores = Column(Integer(), nullable=False)
    op_status = Column(
            Integer(), 
            ForeignKey(
                "status_codes.code_id",
                onupdate="CASCADE",
                ondelete="CASCADE"
            ), 
            nullable=False
        )
    hardware_id = Column(
            Integer(), 
            ForeignKey(
                "hardware.hardware_id",
                onupdate="CASCADE",
                ondelete="CASCADE"
            ), 
            nullable=False
        )   

class sdr(CMDeclarativeBase):
    """
    XXX DESCRIPTION NEEDED
    """

    __tablename__ = "sdr"

    sdr_id = Column(Integer(), Identity(always=True), primary_key=True)
    sdr_serial = Column(CHAR(7), nullable=False, unique=True)
    mboard_name = Column(String(255), nullable=False)
    external_clock = Column(Boolean(), nullable=False)
    op_status = Column(
            Integer(), 
            ForeignKey(
                "status_codes.code_id",
                onupdate="CASCADE",
                ondelete="CASCADE"
            ), 
            nullable=False
        )
    hardware_id = Column(
            Integer(), 
            ForeignKey(
                "hardware.hardware_id",
                onupdate="CASCADE",
                ondelete="CASCADE"
            ), 
            nullable=False
        )

class wrlen(CMDeclarativeBase):
    """
    XXX DESCRIPTION NEEDED
    """

    __tablename__ = "wrlen"

    wr_id = Column(Integer(), Identity(always=True), primary_key=True)
    wr_serial = Column(String(100), nullable=True, unique=True)
    wr_ip = Column(INET(), nullable=True)
    wr_mac = Column(MACADDR(), nullable=True)
    mode = Column(String(100), nullable=True)
    wr_host = Column(String(100), nullable=True)
    op_status = Column(
            Integer(), 
            ForeignKey(
                "status_codes.code_id",
                onupdate="CASCADE",
                ondelete="CASCADE"
            ), 
            nullable=False
        )
    hardware_id = Column(
            Integer(), 
            ForeignKey(
                "hardware.hardware_id",
                onupdate="CASCADE",
                ondelete="CASCADE"
            ), 
            nullable=False
        )

class metadata(CMDeclarativeBase):
    """
    Table that outlines recordings' metadata.

    Attributes:
    -----------
    metadata_id : String Column
        Identification for each sensor. The id is of notation 'hns-XXX'
        where hns = Hcro-Nrdz Sensor. Primary key.
    org : String Column
        Description TBD
    hostname : String Column
        DNS hostname.
    loc : String Column
        Physical location of each sensor at HCRO.
    frequency : BigInteger Column
        Sampling frequency of the USRP.
    sample_rate : BigInteger Column
        Sampling rate of the USRP.
    length : BigInteger Column
        Length of a I/Q data recording in seconds. 
        Current HCRO length: 1 second.
    interval : BigInteger Column
        Time between each recording in seconds. 
        Current HCRO interval: 10 seconds.
    bit_depth : BigInteger Column
        How the data is stored. 
        Current data is stored as signed 16 bit integers.
    """

    __tablename__ = "metadata"
    
    metadata_id = Column(Integer(), Identity(always=True), primary_key=True)
    org = Column(String(100), nullable=False, unique=True)
    frequency = Column(BigInteger(), nullable=False, unique=True)
    sample_rate = Column(BigInteger(), nullable=False, unique=True)
    bandwidth = Column(BigInteger(), nullable=False, unique=True)
    gain = Column(Integer(), nullable=False, unique=True)
    length = Column(Numeric(), nullable=False, unique=True)
    interval = Column(Numeric(), nullable=False, unique=True)
    bit_depth = Column(String(10), nullable=True, unique=True)

    #uc_metadata = UniqueConstraint(
    #        "org", 
    #        "frequency", 
    #        "sample_rate", 
    #        "bandwidth", 
    #        "gain",
    #        "length",
    #        "interval",
    #        "bit_depth"
    #)

class recordings(CMDeclarativeBase):
    """
    Table outlining the data structure of the sensors.

    Attributes:
    -----------
    id : String Column
        Identification for each sensor. The id is of notation 'hns-XXX'
        where hns = Hcro-Nrdz Sensor.
    hardware_id : String Column
        Foreign key from hardware table.
    metadata_id : String Column
        Foreign key from metadata table.
    filename : String Column
        Name of the recordings file.
    filepath : String Column
        Recordings file location.
    created_at : Timestamp
        Time at which the data file was created.
    entered_at : Timestamp
        Time at which the data file was entered into the server.
    survey_id : String Column
        Observing group that the data file was a part of.
    """

    __tablename__ = "recordings"
    
    recording_id = Column(Integer(),Identity(always=True), primary_key=True)
    hardware_id = Column(
            Integer(), 
            ForeignKey(
                "hardware.hardware_id",
                onupdate="CASCADE",
                ondelete="CASCADE"
            ), 
            nullable=False
        )
    metadata_id = Column(
            Integer(), 
            ForeignKey(
                "metadata.metadata_id",
                onupdate="CASCADE",
                ondelete="CASCADE"
            ), 
            nullable=False
        )
    filename = Column(String(100), nullable=False, unique=True)
    filepath = Column(String(255), nullable=False)
    survey_id = Column(CHAR(6), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    entered_at = Column(DateTime(timezone=True), nullable=False)
    
class outputs(CMDeclarativeBase):
    """
    XXX DESCRIPTION NEEDED
    """
    __tablename__ = "outputs"

    output_id = Column(BigInteger(), Identity(always=True), primary_key=True)
    recording_id = Column(
            Integer(), 
            ForeignKey(
                "recordings.recording_id",
                onupdate="CASCADE",
                ondelete="CASCADE"
            ), 
            nullable=False, 
            unique=True
        )
    average_db = Column(Numeric(21,16), nullable=False)
    max_db = Column(Numeric(21,16), nullable=False)
    median_db = Column(Numeric(21,16), nullable=False)
    std_dev = Column(Numeric(), nullable=False)
    kurtosis = Column(Numeric(), nullable=False)

