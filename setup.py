# Copyright (c) 2021, Madawa Soysa
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from setuptools import setup, find_packages


def read(f):
    return open(os.path.join(os.path.dirname(__file__), f)).read()


setup(
    name="marketdata",
    version="0.0.1",
    author="Madawa Soysa",
    author_email="madawa.rc@gmail.com",
    license="Apache 2.0",
    url="https://github.com/madawas/market-analysis",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 1 - Planning",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Version Control :: Git"
    ],
    packages=find_packages(exclude=["tests", "tests.*"]),
    long_description=read("README.rst"),
    install_requires=[
        "pyyaml~=5.4.1",
        "requests~=2.25.1",
        "requests-html~=0.10.0",
        "yahoo-fin~=0.8.6"
    ],
    extras_require={
        "test": [
            "pytest"
        ]
    },
    package_data={
        '': ['LICENSE.txt'],
        'conf': ['conf/config.yaml']
    },
    include_package_data=True
)
