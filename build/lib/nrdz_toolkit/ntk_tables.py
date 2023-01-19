# -*- mode: python; coding: utf-8 -*-
# Copyright 2022 David R. DeBoer
# Licensed under the 2-clause BSD license.

"""All of the :tables defined here."""

from astropy.time import Time
from sqlalchemy import BigInteger, Column, DateTime, Float, ForeignKey, ForeignKeyConstraint, Integer, Numeric, String, Text, func
from sqlalchemy.orm import relationship
from . import CMDeclarativeBase, NotNull
import copy

class hardware(CMDeclarativeBase):
    """
    A table that logs the fixed hardware parameters of the HCRO-NRDZ sensors.

    Attributes
    ----------
    id : String Column
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

    hardware_id = Column(String(20), primary_key = True)
    location = Column(String(30))
    hostname = Column(String(20))
    nfs_mnt = Column(String(60))
    wr_mac = Column(String(20))
    rpi_mac = Column(String(20))
    wr_ip = Column(String(15))
    rpi_ip = Column(String(15))
    usrp_sn = Column(String(20))

    status = relationship('status')
    recordings = relationship('recordings')

    @classmethod
    def create(cls, hardware_id, location, hostname, nfs_mnt, wr_mac, 
            rpi_mac, wr_ip, rpi_ip, usrp_sn):
        return cls(
                hardware_id = hardware_id,
                location = location,
                hostname = hostname,
                nfs_mnt = nfs_mnt, 
                wr_mac = wr_mac,
                rpi_mac = rpi_mac, 
                wr_ip = wr_ip,
                rpi_ip = rpi_ip,
                usrp_sn = usrp_sn
        )

class status(CMDeclarativeBase):
    """
    Table that shows the current status of the unfixed sensor parameters.

    Attributes:
    -----------
    id : String Column
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
    
    """
       
    __tablename__ = "status"

    status_id = Column(String(20), 
            primary_key = True
        )
    time = Column(DateTime(), primary_key = True)
    rpi_cpu_temp = Column(Numeric())
    cpu_usage = Column(Numeric())
    avg_cpu_usage = Column(Numeric())
    bytes_recorded = Column(BigInteger())
    storage_cap = Column(Numeric())
    hardware_id = Column(String(20), ForeignKey('hardware.hardware_id')) 

class metadata(CMDeclarativeBase):
    """
    Table that outlines recordings' metadata.

    Attributes:
    -----------
    id : String Column
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
    
    metadata_id = Column(String(20), primary_key = True)
    org = Column(String(100))
    frequency = Column(BigInteger())
    sample_rate = Column(BigInteger())
    bandwidth = Column(BigInteger())
    gain = Column(Integer())
    length = Column(Numeric())
    interval = Column(Numeric())
    bit_depth = Column(String(10))

    recordings = relationship('recordings')

    @classmethod
    def create(cls, metadata_id, org, frequency, sample_rate, bandwidth, gain, 
            length, interval, bit_depth):
        return cls(
                metadata_id = metadata_id,
                org = org,
                frequency = frequency,
                sample_rate = sample_rate,
                bandwidth = bandwidth,
                gain = gain,
                length = length,
                interval = interval,
                bit_depth = bit_depth
        )

class recordings(CMDeclarativeBase):
    """
    Table outlining the data structure of the sensors.

    Attributes:
    -----------
    id : String Column
        Identification for each sensor. The id is of notation 'hns-XXX'
        where hns = Hcro-Nrdz Sensor.
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
    
    recordings_id = Column(String(20), primary_key=True)
    hardware_id = Column(String(20), ForeignKey('hardware.hardware_id'))
    metadata_id = Column(String(20), ForeignKey('metadata.metadata_id'))
    filename = Column(String(100))
    filepath = Column(String(255))
    created_at = Column(DateTime())
    entered_at = Column(DateTime())
    survey_id = Column(String(20))

    @classmethod
    def create(cls, recordings_id, hardware_id, metadata_id, filename, 
            filepath, created_at, entered_at, survey_id):
        return cls(
                recordings_id = recordings_id,
                filename = filename,
                filepath = filepath,
                created_at = created_at,
                entered_at = entered_at,
                survey_id = survey_id
        )
