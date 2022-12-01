# -*- mode: python; coding: utf-8 -*-
# Copyright 2022 David R. DeBoer
# Licensed under the 2-clause BSD license.

"""All of the tables defined here."""

from astropy.time import Time
from sqlalchemy import BigInteger, Column, Float, ForeignKey, ForeignKeyConstraint, String, Text, Float, func
from . import CMDeclarativeBase, NotNull
import copy

class hardware_fixed(CMDeclarativeBase):
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
    amp : String Column
        Type of amplifier used in the sensor.
    ant : String Column
        Type of antenna used in the sensor.

    """

    __tablename__ = "hardware_fixed"

    id = Column(String(10), primary_key=True)
    loc = Column(String(50))
    hostname = Column(String(20))
    nfs_mnt = Column(String(20))
    wr_mac = Column(String(20))
    rpi_mac = Column(String(20))
    ant = Column(String(20))
    amp = Column(String(20))

    @classmethod
    def create(cls, id, loc, hostname, nfs_mnt, wr_mac, rpi_mac, ant, amp):
        return cls(
                id = id,
                loc = loc,
                hostname = hostname,
                nfs_mnt = nfs_mnt, 
                wr_mac = wr_mac,
                rpi_mac = rpi_mac, 
                ant = ant,
                amp = amp
        )

class hardware_status(CMDeclarativeBase):
    """
    Table that shows the current status of the unfixed parameters of a sensor.

    Attributes:
    -----------
    id : String Column
        Identification for each sensor. The id is of notation 'hns-XXX'
        where hns = Hcro-Nrdz Sensor. Primary key. Foreign key with hardware_fixed.
    time : Integer Column
        Timestamp in unix time at which the information was collected.
        Primary key.
    rpi_temp : Float Column
        Raspberry Pi temperature.
    usrp_temp : Float Column
        Universal Software Radio Peripheral temperature.
    wr_temp : Float Column
        White Rabbit temperature.
    storage : Float Column
        Remaining storage on raspberry pi.
    
    """
       
    __tablename__ = "hardware_status"

    id = Column(String(10), ForeignKey('hardware_fixed.id'), primary_key=True)
    time = Column(BigInteger(), primary_key=True)
    usrp_temp = Column(Float())
    rpi_temp = Column(Float())
    wr_temp = Column(Float())
    storage = Column(Float())

class recordings(CMDeclarativeBase):
    """
    Table outlining the data structure of the sensors.

    Attributes:
    -----------
    id : String Column
        Identification for each sensor. The id is of notation 'hns-XXX'
        where hns = Hcro-Nrdz Sensor. Primary key. Foreign key with hardware_fixed.
    filename : String Column
        Name of the recordings file.
    filepath : String Column
        Recordings file location.
    datetime : String Column
        Two recordings timestamps, one for when the recording (I/Q data) is created,
        and another automatically generated timestamp for when the link is added to
        the database.
    group : String Column
        (Optional) The idea behind this column would be to categorize
        I/Q data recordings into specific surveys for specific amounts of time.
    """

    __tablename__ = "recordings"
    
    id = Column(String(10), ForeignKey('hardware_fixed.id'), primary_key=True)
    filename = Column(String(20))
    filepath = Column(String(50))
    datetime = Column(String(30))
    group = Column(String(20))

    @classmethod
    def create(cls, id, filename, filepath, datetime, group):
        return cls(
                id = id,
                filename = filename,
                filepath = filepath,
                datetime = datetime,
                group = group
        )

class hardware_config(CMDeclarativeBase):
    """
    Table outlining the data structure of the sensors.

    Attributes:
    -----------
    id : String Column
        Identification for each sensor. The id is of notation 'hns-XXX'
        where hns = Hcro-Nrdz Sensor. Primary key. Foreign key with hardware_fixed.
    org : String Column
        Description TBD
    hostname : String Column
        DNS hostname.
    usrp_sn : String Column
        USRP serial number.
    loc : String Column
        Physical location of each sensor at HCRO.
    frequency : BigInteger Column
        Sampling frequency of the USRP.
    sample_rate : BigInteger Column
        Sampling rate of the USRP.
    length : BigInteger Column
        Length of a I/Q data recording in seconds. Current HCRO length: 1 second.
    interval : BigInteger Column
        Time between each recording in seconds. Current HCRO interval: 10 seconds.
    bit_depth : BigInteger Column
        How the data is stored. Current data is stored as signed 16 bit integers.
    """

    __tablename__ = "hardware_config"
    
    id = Column(String(10), ForeignKey('hardware_fixed.id'), primary_key=True)
    org = Column(String(20))
    hostname = Column(String(20))
    usrp_sn = Column(String(20))
    loc = Column(String(50))
    frequency = Column(BigInteger())
    sample_rate = Column(BigInteger())
    gain = Column(BigInteger())
    length = Column(BigInteger())
    interval = Column(BigInteger())
    bit_depth = Column(BigInteger())

    @classmethod
    def create(cls, id, org, hostname, usrp_sn, loc, frequency, sample_rate, gain, 
            length, interval, bit_depth):
        return cls(
                id = id,
                hostname = hostname,
                usrp_sn = usrp_sn,
                loc = loc,
                frequency = frequency,
                sample_rate = sample_rate,
                gain = gain,
                length = length,
                interval = interval,
                bit_depth = bit_depth
        )
