#! /usr/bin/env python
# -*- mode: python; coding: utf-8 -*-
# Copyright 2022 
# Licensed under the 2-clause BSD license.

"""Module setup."""

import glob
import io
from setuptools import setup


with io.open("README.md", "r", encoding="utf-8") as readme_file:
    readme = readme_file.read()

setup_args = {
    "name": "nrdz_toolkit",
    "description": "nrdz_toolkit: tools for viewing, manipulating, etc",
    "long_description": readme,
    "url": "https://github.com/i",
    "license": "BSD",
    "author": "David R. DeBoer",
    "author_email": "ddeboer@berkeley.edu",
    "packages": ["nrdz_toolkit"],
    "scripts": glob.glob("scripts/*"),
    "include_package_data": True,
    "install_requires": [
        "alembic",
        "astropy",
        "geoalchemy2",
        "numpy",
        "psycopg2-binary",
        "redis",
        "setuptools_scm",
        "sqlalchemy",
    ],
    "extras_require": {
        "sqlite": ["tabulate"],
        "all": ["h5py", "pandas", "psutil", "python-dateutil", "tabulate"],
        "dev": [
            "h5py",
            "pandas",
            "psutil",
            "python-dateutil",
            "tabulate",
            "pytest",
            "pre-commit",
        ],
    },
    "classifiers": [
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Scientific/Engineering",
    ],
}

if __name__ == "__main__":
    setup(**setup_args)
