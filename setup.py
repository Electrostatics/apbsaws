#!/usr/bin/python3

"""
The use of continuum solvation methods such as APBS requires accurate and
complete structural data as well as force field parameters such as atomic
charges and radii. Unfortunately, the limiting step in continuum electrostatics
calculations is often the addition of missing atomic coordinates to molecular
structures from the Protein Data Bank and the assignment of parameters to these
structures. To adds this problem, we have developed PDB2PQR. This software
automates many of the common tasks of preparing structures for continuum
solvation calculations as well as many other types of biomolecular structure
modeling, analysis, and simulation. These tasks include:

* Adding a limited number of missing heavy (non-hydrogen) atoms to biomolecular
  structures.
* Estimating titration states and protonating biomolecules in a manner
  consistent with favorable hydrogen bonding.
* Assigning charge and radius parameters from a variety of force fields.
* Generating "PQR" output compatible with several popular computational
  modeling and analysis packages.

This service is intended to facilitate the setup and execution of
electrostatics calculations for both experts and non-experts and thereby
broaden the accessibility of biomolecular solvation and electrostatics analyses
to the biomedical community.
"""

from sys import version_info
from setuptools import find_packages, setup

# NOTE: The following reads the version number and makes
#       if available to the packaging tools before installation.
#       REF: https://stackoverflow.com/questions/458550/standard-way-to-embed-version-into-python-package  # noqa: E501
#       This makes __version__ valid below
with open("lambda_services/_version.py") as fobj:
    exec(fobj.read())

if version_info[:2] < (3, 6):
    raise RuntimeError("Python version >= 3.6 is required.")

with open("README.md", "r") as fobj:
    LONG_DESCRIPTION = fobj.read()

setup(
    name="lambda_services",
    version=__version__,  # noqa: F821
    author="Nathan Baker, Elvis Offer, Matt Macduff, and Darren Curtis.",
    author_email="nathanandrewbaker@gmail.com",
    description=(
        "Automates many of the common tasks of preparing structures for "
        "continuum solvation calculations as well as many other types of "
        "biomolecular structure modeling, analysis, and simulation."
    ),
    long_description=LONG_DESCRIPTION,
    install_requires=[
        "urllib3==1.26.3",
    ],
    url="http://www.poissonboltzmann.org",
    python_requires=">=3.6",
    extras_require={
        "dev": ["check-manifest"],
        "test": [
            "black",
            "boto3",
            "coverage",
            "flake8",
            "moto",
            "pandas >= 1.0",
            "pylint",
            "pytest",
            "pytest-cov",
            "testfixtures",
        ],
    },
    tests_require=[
        "pandas >= 1.0",
        "pytest",
        "testfixtures",
    ],
    test_suite="tests",
    license="BSD",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Chemistry",
    ],
    project_urls={
        "Documentation": "https://apbs-aws.readthedocs.io/",
        "Get help": "https://github.com/Electrostatics/apbs-aws/issues",
        "Publications": "https://pubmed.ncbi.nlm.nikh.gov/?term=R01+GM069702",
        "Funding": "https://bit.ly/apbs-funding",
        "Source": "https://github.com/Electrostatics/apbs-aws",
    },
    keywords="science chemistry molecular biology",
)