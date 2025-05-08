# -*- coding: utf-8 -*-
# Copyright (C) 2017-2025 Davide Gessa
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# For detail about GNU see <http://www.gnu.org/licenses/>.
from setuptools import setup

setup(
    name="weatherrouting",
    version="0.2.3",
    description="Weather routing library for sailing",
    author="Davide Gessa",
    setup_requires="setuptools",
    author_email="gessadavide@gmail.com",
    packages=["weatherrouting", "weatherrouting.routers"],
    install_requires=["latlon3"],  # ['geographiclib'],
    test_suite="tests",
)
