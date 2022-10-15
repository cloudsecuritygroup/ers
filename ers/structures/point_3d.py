##
## Copyright 2022 Zachary Espiritu and Evangelia Anna Markatou and
##                Francesca Falzon and Roberto Tamassia and William Schor
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
##    http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
##

import functools

from ..util import serialization


@functools.total_ordering
class Point3D:
    """
    A point representing an integer coordinate in a three-dimensional space.
    """

    def __init__(self, x: int, y: int, z: int):
        self.x = int(x)
        self.y = int(y)
        self.z = int(z)

    def __eq__(self, other):
        if not isinstance(other, Point3D):
            return False
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __lt__(self, other):
        if not isinstance(other, Point3D):
            return NotImplemented
        return self.x < other.x and self.y < other.y and self.z < other.z

    def __hash__(self):
        return hash((self.x, self.y, self.z))

    def __bytes__(self):
        return serialization.ObjectToBytes([self.x, self.y, self.z])

    def __str__(self):
        return f"Point3D({self.x}, {self.y}, {self.z})"

    def __repr__(self):
        return str(self)

    @classmethod
    def from_bytes(self, b: bytes):
        x, y, z = serialization.BytesToObject(b)
        return self(x, y, z)

    def contained_by(self, bottom, top):
        return (
            self.x >= bottom.x
            and self.y >= bottom.y
            and self.z >= bottom.z
            and self.x <= top.x
            and self.y <= top.y
            and self.z <= top.z
        )
