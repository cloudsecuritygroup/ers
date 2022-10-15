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

from .point_3d import Point3D

import functools
import math


@functools.total_ordering
class Rect3D:
    def __init__(self, start: Point3D, end: Point3D):
        """
        Creates a rectangle bounded by the points `start` (inclusive) and
        `end` (exclusive).
        """
        self.start = start
        self.end = end

        if (
            (self.start.x > self.end.x)
            or (self.start.y > self.end.y)
            or (self.start.z > self.end.z)
        ):
            raise ValueError

    def __str__(self):
        return "Rect3D[" + str(self.start) + ", " + str(self.end) + "]"

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash((self.start, self.end))

    def __eq__(self, other):
        if not isinstance(other, Rect3D):
            return False
        return self.start == other.start and self.end == other.end

    def __lt__(self, other):
        if not isinstance(other, Rect3D):
            return NotImplemented
        return self.start < other.start and self.end < other.end

    def __contains__(self, other):
        if isinstance(other, Point3D):
            return self.contains_point(other)
        elif isinstance(other, Rect3D):
            return self.contains_rect(other)
        else:
            return NotImplemented

    def intersects(self, rect) -> bool:
        if not isinstance(rect, Rect3D):
            return False

        l1, r1 = self.start, self.end
        l2, r2 = rect.start, rect.end

        if l1.x == r1.x or l1.y == r1.y or l2.x == r2.x or l2.y == r2.y:
            # the line cannot have positive overlap
            return False

        # If one rectangle is on left side of other
        if l1.x >= r2.x or l2.x >= r1.x:
            return False

        # If one rectangle is above other
        if r1.y >= l2.y or r2.y >= l1.y:
            return False

        return True

    def contains_point(self, point: Point3D) -> bool:
        """
        Returns true if `point` is inside this `Rect`.
        """
        if not isinstance(point, Point3D):
            return False
        return (
            point.x >= self.start.x
            and point.x < self.end.x
            and point.y >= self.start.y
            and point.y < self.end.y
            and point.z >= self.start.z
            and point.z < self.end.z
        )

    def contains_rect(self, rect) -> bool:
        """
        Returns true if `rect` is inside this `Rect`.
        """

        if not isinstance(rect, Rect3D):
            return False

        return (
            rect.start_x() >= self.start.x
            and rect.start_x() < self.end.x
            and rect.start_y() >= self.start.y
            and rect.start_y() < self.end.y
            and rect.start_z() >= self.start.z
            and rect.start_z() < self.end.z
            and rect.end_x() > self.start.x
            and rect.end_x() <= self.end.x
            and rect.end_y() > self.start.y
            and rect.end_y() <= self.end.y
            and rect.end_z() > self.start.z
            and rect.end_z() <= self.end.z
        )

    def contains_rect_brc(self, rect) -> bool:
        """
        Returns true if `rect` is inside this `Rect`.
        """

        if not isinstance(rect, Rect3D):
            return False

        return (
            
            self.start.x <= rect.start.x
            and self.end.x+1 >= rect.end.x
            and self.start.y <= rect.start.y
            and self.end.y+1 >= rect.end.y
            and self.start.z <= rect.start.z
            and self.end.z+1 >= rect.end.z
        )
    def contains_rect_inclusive(self, rect) -> bool:
        """
        Returns true if `rect` is inside this `Rect`.
        """
        if not isinstance(rect, Rect3D):
            return False

        return (
            rect.start_x() >= self.start.x
            and rect.start_x() <= self.end.x
            and rect.start_y() >= self.start.y
            and rect.start_y() <= self.end.y
            and rect.start_z() >= self.start.z
            and rect.start_z() <= self.end.z
            and rect.end_x() >= self.start.x
            and rect.end_x() <= self.end.x
            and rect.end_y() >= self.start.y
            and rect.end_y() <= self.end.y
            and rect.end_z() >= self.start.z
            and rect.end_z() <= self.end.z
        )

    def draw(self, ax, c="k", lw=1, **kwargs):
        """
        Code taken from https://scipython.com/blog/quadtrees-2-implementation-in-python/
        """
        x1, y1 = self.start.x, self.start.y
        x2, y2 = self.end.x, self.end.y
        ax.plot([x1, x2, x2, x1, x1], [y1, y1, y2, y2, y1], c=c, lw=lw, **kwargs)

    def x_length(self) -> int:
        return self.end.x - self.start.x

    def y_length(self) -> int:
        return self.end.y - self.start.y

    def z_length(self) -> int:
        return self.end.z - self.start.z

    def start_x(self) -> int:
        return self.start.x

    def end_x(self) -> int:
        return self.end.x

    def start_y(self) -> int:
        return self.start.y

    def end_y(self) -> int:
        return self.end.y

    def start_z(self) -> int:
        return self.start.z

    def end_z(self) -> int:
        return self.end.z


    def divide(self):
        #print(self.start.x, self.end.x)
        #print(self.start.y, self.end.y)
        x_half = math.floor((self.start.x + self.end.x) / 2)
        y_half = math.floor((self.start.y + self.end.y) / 2)
        z_half = math.floor((self.start.z + self.end.z) / 2)

        #print("half", x_half, y_half)

        if self.end.x-self.start.x >=1 or self.end.y-self.start.y >=1:
            return [
                Rect3D(Point3D(self.start.x, self.start.y, self.start.z), Point3D(x_half, y_half, z_half)),
                Rect3D(Point3D(self.start.x, self.start.y, z_half+1), Point3D(x_half, y_half, self.end.z)),
                Rect3D(Point3D(self.start.x, y_half+1, self.start.z), Point3D(x_half, self.end.y,z_half)),
                Rect3D(Point3D(self.start.x, y_half+1, z_half+1), Point3D(x_half, self.end.y,self.end.z)),
                Rect3D(Point3D(x_half+1, self.start.y,self.start.z), Point3D(self.end.x, y_half,z_half)),
                Rect3D(Point3D(x_half+1, self.start.y,z_half+1), Point3D(self.end.x, y_half,self.end.z)),
                Rect3D(Point3D(x_half+1, y_half+1,self.start.z), Point3D(self.end.x, self.end.y,z_half)),
                Rect3D(Point3D(x_half+1, y_half+1,z_half+1), Point3D(self.end.x, self.end.y,self.end.z)),
            ]
        else:
            return []
