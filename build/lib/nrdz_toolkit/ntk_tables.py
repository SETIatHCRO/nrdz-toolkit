# -*- mode: python; coding: utf-8 -*-
# Copyright 2022 David R. DeBoer
# Licensed under the 2-clause BSD license.

"""All of the tables defined here."""

from astropy.time import Time
from sqlalchemy import BigInteger, Column, ForeignKeyConstraint, String, Text, Float, func
from . import CMDeclarativeBase, NotNull, ntk
import copy

class hardware_table(CMDeclarativeBase):
    """
    A table that logs the unique hardware parameters of each NRDZ sensor.

    Attributes
    ----------
    id : String Column
        Unique id for each sensor of notation 'hnsXXX' where hns = Hat creek Nrdz Sensor
        followed by a designated number. Primary_key
    wr_mac : String Column
        White rabbit mac address.
    rpi_mac : String Column
        Raspberry Pi mac address.
    hostname : String Column
        DNS hostname.
    nfs_mnt: String Column
        Network File System mount.

    """

    __tablename__ = "hardware_table"
    
    id = Column(String(10), primary_key=True)
    wr_mac = Column(String(20))
    rpi_mac = Column(String(20))
    hostname = Column(String(20))
    nfs_mnt = Column(String(30))
