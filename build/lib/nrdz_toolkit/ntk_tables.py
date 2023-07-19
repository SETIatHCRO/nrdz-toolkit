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
from sqlalchemy.sql import func
from . import CMDeclarativeBase, NotNull
import copy

class status_codes(CMDeclarativeBase):
    """
    The operational statuses of a sensor using a system of
    integers ranging from 0-9, with each integer corresponding to a
    different status.

    Attributes:
    -----------
    code_id : Integer Column
        Integer from 0-9. Primary key.
    description : Text Column
        Status description.
    """

    __tablename__ = "status_codes"
    
    code_id = Column(Integer(), nullable=False, primary_key=True)
    description = Column(Text(), nullable=False)

class storage(CMDeclarativeBase):
    """
    Information relating to server storage.

    Attributes:
    -----------
    mount_id : Integer Column
        Primary key.
    nfs_mnt : String Column
        Network File System. A distributed file system that allows users
        to access files and directories located on remote computers and
        treat them as if they were local.
    local_mnt : String Column
    storage_cap : BigInteger Column
        Amount of storage left on mount.
    op_status : Integer Column
        See table status_codes.
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
    location : Point Column
        Physical location of each sensor at HCRO in lat/long coordinates.
    enclosure : Boolean Column
        Determines if device is enclosed within the EMI box.
        0 for "not enclosed", 1 for "enclosed".
    mount_id : Integer Column
    op_status : Integer Column
        See table status_codes.
    """

    __tablename__ = "hardware"

    hardware_id = Column(Integer(), Identity(always=True), primary_key=True)
    location = Column(String(100), nullable=False)
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
    status_id : Integer Column.
        Primary key.
    hostname : String Column
    time : Timestamp Column
        Timestamp in local time at which the information was collected.
    rpi_cpu_temp : Numeric Column
        Raspberry Pi CPU temperature.
    sdr_temp : Numeric Column
        Software defined radio temperature.
    avg_cpu_usage : Float Column.
        Average CPU usage over time.
    bytes_recorded : BigInteger Column
        Number of bytes recorded. Unsure if this is for a single capture or 
        over the course of an observation. FOLLOWUP NEEDED
    rem_nfs_storage_cap : BigInteger Column
        Remaining storage on the nfs mount.
    rem_rpi_storage_cap : BigInteger Column
        Remaining storage on the raspberry pi.
    rpi_uptime_minutes : BigInteger Column
    hardware_id : String Column
        Foreign key from hardware table.
    wr_servo_state : String Column
    wr_sfp1_link : Boolean Column
    wr_sfp2_link : Boolean Column
    wr_sfp1_tx : BigInteger Column
    wr_sfp2_tx : BigInteger Column
    wr_sfp1_rx : BigInteger Column
    wr_sfp2_rx : BigInteger Column
    wr_phase_setp : Integer Column
    wr_rtt : Integer Column
    wr_crtt : Integer Column
    wr_clck_offset : Integer Column
    wr_updt_cnt : Integer Column
    wr_temp : Numeric Column
    wr_host : String Column
    """
       
    __tablename__ = "status"

    status_id = Column(BigInteger(), Identity(always=True), primary_key=True)
    hostname = Column(String(100), nullable=False)
    time = Column(DateTime(timezone=True), default=func.current_timestamp())
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
    Information about the Raspberry Pi's of each sensor.

    Attributes:
    -----------
    rpi_id : Integer Column
        Primary key.
    hostname : String Column
    rpi_ip : INET Column
        Raspberry pi IP address.
    rpi_mac : MACADDR Column
        Raspberry pi MAC address
    rpi_v : String Column
        Raspberry pi version.
    os_v : String Column
        Operating system version.
    memory : BigInteger Column
    storage_cap : BigInteger Column
    cpu_type : String Column
    cpu_cores : Integer Column
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
    cpu_type = Column(String(255), nullable=False)
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

class outputs(CMDeclarativeBase):
    """
    XXX DESCRIPTION NEEDED
    """
    __tablename__ = "outputs"

    output_id = Column(BigInteger(), Identity(always=True), primary_key=True)
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
    created_at = Column(DateTime(timezone=True), nullable=False)
    average_db = Column(Numeric(21,16), nullable=False)
    max_db = Column(Numeric(21,16), nullable=False)
    median_db = Column(Numeric(21,16), nullable=False)
    std_dev = Column(Numeric(), nullable=False)
    kurtosis = Column(Numeric(), nullable=False)
    output_path = Column(String(255), nullable=True)

