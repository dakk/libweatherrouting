# -*- coding: utf-8 -*-
# Copyright (C) 2017-2024 Davide Gessa
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
import datetime
import random


class MockGrib:
    def __init__(self, starttws, starttwd, fuzziness, out_of_scope=None):
        self.starttws = starttws
        self.starttwd = starttwd
        self.fuzziness = fuzziness
        self.out_of_scope = out_of_scope
        self.seedSource = datetime.datetime.fromisoformat("2000-01-01T00:00:00")

    def tws_var(self, t=None):
        if t:
            delta = t - self.seedSource
            random.seed(delta.total_seconds())
        return self.starttws + self.starttws * (
            random.random() * self.fuzziness - self.fuzziness / 2
        )

    def twd_var(self, t=None):
        if t:
            delta = t - self.seedSource
            random.seed(delta.total_seconds())
        return self.starttwd + self.starttwd * (
            random.random() * self.fuzziness - self.fuzziness / 2
        )

    def getWindAt(self, t, lat, lon):
        if not self.out_of_scope or t < self.out_of_scope:
            return (
                self.twd_var(t),
                self.tws_var(t),
            )
        else:
            return None
