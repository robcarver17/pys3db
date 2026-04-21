from __future__ import print_function
import os
from setuptools import setup, find_packages


def read(fname):
    """Utility function to read the README file."""
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def dir_this_file():
    return os.path.dirname(os.path.realpath(__file__))


setup(
    name="pys3db",
    version="1.0.0",
    author="Robert Carver",
    description=("Simple python SQLLITE3 wrapper"),
    url="https://github.com/robcarver17/pys3db",
    packages=find_packages(),
    long_description=read("README.md"),
    extras_require=dict(),
)
