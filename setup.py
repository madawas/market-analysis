import os
from setuptools import setup


def read(f):
    return open(os.path.join(os.path.dirname(__file__), f)).read()


setup(
    name="marketdata",
    version="0.0.1",
    author="Madawa Soysa",
    author_email="madawa.rc@gmail.com",
    license="Apache 2.0",
    url="http://packages.python.org/an_example_pypi_project",
    packages=["marketdata"],
    long_description=read("README.rst"),
    include_package_data=True
)
