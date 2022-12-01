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

    __tablename__ = "recordings"
    
    id = Column(String(10), ForeignKey('hardware_fixed.id'), primary_key=True)
    filename = Column(String(20))
    filepath = Column(String(50))
    datetime = Column(String(30))
    group = Column(String(20))

class hardware_config(CMDeclarativeBase):

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

