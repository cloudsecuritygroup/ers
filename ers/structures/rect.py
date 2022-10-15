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
import math

from .point import Point


@functools.total_ordering
class Rect:
    def __init__(self, start: Point, end: Point):
        """
        Creates a rectangle bounded by the points `start` (inclusive) and
        `end` (exclusive).
        """
        self.start = start
        self.end = end

        if (self.start.x > self.end.x) or (self.start.y > self.end.y):
            raise ValueError

    def __str__(self):
        return "Rect[" + str(self.start) + ", " + str(self.end) + "]"

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash((self.start, self.end))

    def __eq__(self, other):
        if not isinstance(other, Rect):
            return False
        return self.start == other.start and self.end == other.end

    def __lt__(self, other):
        if not isinstance(other, Rect):
            return NotImplemented
        return self.start < other.start and self.end < other.end

    def __contains__(self, other):
        if isinstance(other, Point):
            return self.contains_point(other)
        elif isinstance(other, Rect):
            return self.contains_rect(other)
        else:
            return NotImplemented

    def intersects(self, rect) -> bool:
        if not isinstance(rect, Rect):
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

    def contains_point(self, point: Point) -> bool:
        """
        Returns true if `point` is inside this `Rect`.
        """
        if not isinstance(point, Point):
            return False
        return (
            point.x >= self.start.x
            and point.x < self.end.x
            and point.y >= self.start.y
            and point.y < self.end.y
        )

    def contains_rect(self, rect) -> bool:
        """
        Returns true if `rect` is inside this `Rect`.
        """

        if not isinstance(rect, Rect):
            return False

        return (
            rect.start_x() >= self.start.x
            and rect.start_x() < self.end.x
            and rect.start_y() >= self.start.y
            and rect.start_y() < self.end.y
            and rect.end_x() > self.start.x
            and rect.end_x() <= self.end.x
            and rect.end_y() > self.start.y
            and rect.end_y() <= self.end.y
        )

    def contains_rect_inclusive(self, rect) -> bool:
        """
        Returns true if `rect` is inside this `Rect`.
        """
        if not isinstance(rect, Rect):
            return False

        return (
            rect.start_x() >= self.start.x
            and rect.start_x() <= self.end.x
            and rect.start_y() >= self.start.y
            and rect.start_y() <= self.end.y
            and rect.end_x() >= self.start.x
            and rect.end_x() <= self.end.x
            and rect.end_y() >= self.start.y
            and rect.end_y() <= self.end.y
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

        #print("half", x_half, y_half)

        if self.end.x-self.start.x >=1 or self.end.y-self.start.y >=1:
            return [
                Rect(Point(self.start.x, self.start.y), Point(x_half, y_half)),
                Rect(Point(self.start.x, y_half+1), Point(x_half, self.end.y)),
                Rect(Point(x_half+1, self.start.y), Point(self.end.x, y_half)),
                Rect(Point(x_half+1, y_half+1), Point(self.end.x, self.end.y)),
            ]
        else:
            return []








