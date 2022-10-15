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
class Point:
    """
    A point representing an integer coordinate in a two-dimensional space.
    """

    def __init__(self, x: int, y: int):
        self.x = int(x)
        self.y = int(y)

    def __eq__(self, other):
        if not isinstance(other, Point):
            return False
        return self.x == other.x and self.y == other.y

    def __lt__(self, other):
        if not isinstance(other, Point):
            return NotImplemented
        return self.x < other.x and self.y < other.y

    def __hash__(self):
        return hash((self.x, self.y))

    def __bytes__(self):
        return serialization.ObjectToBytes([self.x, self.y])

    def __str__(self):
        return "Point(" + str(self.x) + ", " + str(self.y) + ")"

    def __repr__(self):
        return str(self)

    @classmethod
    def from_bytes(self, b: bytes):
        x, y = serialization.BytesToObject(b)
        return self(x, y)

    def contained_by(self, bottom, top):
        return (
            self.x >= bottom.x
            and self.y >= bottom.y
            and self.x <= top.x
            and self.y <= top.y
        )
