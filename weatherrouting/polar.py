# -*- coding: utf-8 -*-
# Copyright (C) 2017-2025 Davide Gessa
# Copyright (C) 2021 Enrico Ferreguti
# Copyright (C) 2012 Riccardo Apolloni
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
import math
from io import TextIOWrapper
from typing import Dict, Optional, Tuple


class Polar:
    def __init__(self, polar_path: str, f: Optional[TextIOWrapper] = None):
        """
        Parameters
        ----------
        polar_path : string
                Path of the polar file
        f : File
                File object for passing an opened file
        """

        self.tws = []
        self.twa = []
        self.vmgdict: Dict[Tuple[float, float], Tuple[float, float]] = {}
        self.speed_table = []

        if f is None:
            f = open(polar_path, "r")

        tws = f.readline().split()
        for i in range(1, len(tws)):
            self.tws.append(float(tws[i].replace("\x02", "")))

        line = f.readline()
        while line != "":
            data = line.split()
            twa = float(data[0])
            self.twa.append(math.radians(twa))
            speedline = []
            for i in range(1, len(data)):
                speed = float(data[i])
                speedline.append(speed)
            self.speed_table.append(speedline)
            line = f.readline()
        f.close()

    def to_string(self) -> str:
        s = "TWA\\TWS"
        for x in self.tws:
            s += f"\t{x:.0f}"
        s += "\n"

        l_idx = 0
        for y in self.twa:
            s += f"{round(math.degrees(y))}"
            sl = self.speed_table[l_idx]

            for x in sl:
                s += f"\t{x:.1f}"
            s += "\n"

            l_idx += 1

        return s

    def get_speed(self, tws: float, twa: float) -> float:  # noqa: C901
        """Returns the speed (in knots) given tws (in knots) and twa (in radians)"""

        tws1 = 0
        tws2 = 0

        for k in range(0, len(self.tws)):
            if tws >= self.tws[k]:
                tws1 = k
        for k in range(len(self.tws) - 1, 0, -1):
            if tws <= self.tws[k]:
                tws2 = k
        if tws1 > tws2:  # TWS over table limits
            tws2 = len(self.tws) - 1
        twa1 = 0
        twa2 = 0
        for k in range(0, len(self.twa)):
            if twa >= self.twa[k]:
                twa1 = k
        for k in range(len(self.twa) - 1, 0, -1):
            if twa <= self.twa[k]:
                twa2 = k

        speed1 = self.speed_table[twa1][tws1]
        speed2 = self.speed_table[twa2][tws1]
        speed3 = self.speed_table[twa1][tws2]
        speed4 = self.speed_table[twa2][tws2]

        if twa1 != twa2:
            speed12 = speed1 + (speed2 - speed1) * (twa - self.twa[twa1]) / (
                self.twa[twa2] - self.twa[twa1]
            )  # interpolazione su twa
            speed34 = speed3 + (speed4 - speed3) * (twa - self.twa[twa1]) / (
                self.twa[twa2] - self.twa[twa1]
            )  # interpolazione su twa
        else:
            speed12 = speed1
            speed34 = speed3
        if tws1 != tws2:
            speed = speed12 + (speed34 - speed12) * (tws - self.tws[tws1]) / (
                self.tws[tws2] - self.tws[tws1]
            )
        else:
            speed = speed12
        return speed

    def get_reaching(self, tws: float) -> Tuple[float, float]:
        maxspeed = 0.0
        twamaxspeed = 0.0
        for twa_ in range(0, 181):
            twa = math.radians(twa_)
            speed = self.get_speed(tws, twa)
            if speed > maxspeed:
                maxspeed = speed
                twamaxspeed = twa
        return (maxspeed, twamaxspeed)

    def get_max_vmgtwa(self, tws: float, twa: float) -> Tuple[float, float]:
        if (tws, twa) not in self.vmgdict:
            twamin = max(0, twa - math.pi / 2)
            twamax = min(math.pi, twa + math.pi / 2)
            alfa = twamin
            maxvmg = -1.0
            while alfa < twamax:
                v = self.get_speed(tws, alfa)
                vmg = v * math.cos(alfa - twa)
                if vmg - maxvmg > 10**-3:  # 10**-3 errore tollerato
                    maxvmg = vmg
                    twamaxvmg = alfa
                alfa = alfa + math.radians(1)
            self.vmgdict[tws, twa] = (maxvmg, twamaxvmg)
        return self.vmgdict[(tws, twa)]

    def get_max_vmg_up(self, tws: float) -> Tuple[float, float]:
        vmguptupla = self.get_max_vmgtwa(tws, 0)
        return (vmguptupla[0], vmguptupla[1])

    def get_max_vmg_down(self, tws: float) -> Tuple[float, float]:
        vmgdowntupla = self.get_max_vmgtwa(tws, math.pi)
        return (-vmgdowntupla[0], vmgdowntupla[1])

    def get_routage_speed(self, tws, twa) -> float:
        up = self.get_max_vmg_up(tws)
        vmgup = up[0]
        twaup = up[1]
        down = self.get_max_vmg_down(tws)
        vmgdown = down[0]
        twadown = down[1]
        v = 0.0

        if twa >= twaup and twa <= twadown:
            v = self.get_speed(tws, twa)
        else:
            if twa < twaup:
                v = vmgup / math.cos(twa)
            if twa > twadown:
                v = vmgdown / math.cos(twa)
        return v

    def get_twa_routage(self, tws: float, twa: float) -> float:
        up = self.get_max_vmg_up(tws)
        # vmgup = up[0]
        twaup = up[1]
        down = self.get_max_vmg_down(tws)
        # vmgdown = down[0]
        twadown = down[1]
        if twa >= twaup and twa <= twadown:
            pass
            # twa = twa
        else:
            if twa < twaup:
                twa = twaup
            if twa > twadown:
                twa = twadown
        return twa
