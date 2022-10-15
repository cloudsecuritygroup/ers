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

from .rect import Rect
from .point import Point

from typing import Dict, List, Set

import math

QDAG_ROOT = "__root__"


def get_quad_divisions(rect: Rect) -> List[Rect]:
    """
    Returns the 4 quad tree divisions.
    """
    this_start_x = rect.start_x()
    this_start_y = rect.start_y()
    this_width = rect.x_length()
    this_height = rect.y_length()

    child_width = int(this_width / 2)
    child_height = int(this_height / 2)

    southwest = Rect(
        Point(this_start_x, this_start_y),
        Point(this_start_x + child_width, this_start_y + child_height),
    )
    northwest = Rect(
        Point(this_start_x, this_start_y + child_height),
        Point(this_start_x + child_width, this_start_y + (child_height * 2)),
    )
    northeast = Rect(
        Point(this_start_x + child_width, this_start_y + child_height),
        Point(this_start_x + (child_width * 2), this_start_y + (child_height * 2)),
    )
    southeast = Rect(
        Point(this_start_x + child_width, this_start_y),
        Point(this_start_x + (child_width * 2), this_start_y + child_height),
    )
    return [southwest, northwest, northeast, southeast]


def get_intermediate_divisions(rect: Rect) -> List[Rect]:
    """
    Returns the 5 SRC intermediate nodes.
    """
    this_start_x = rect.start_x()
    this_start_y = rect.start_y()
    this_width = rect.x_length()
    this_height = rect.y_length()

    child_width = int(this_width / 2)
    child_height = int(this_height / 2)

    half_child_width = int(child_width / 2)
    half_child_height = int(child_height / 2)

    north = Rect(
        Point(this_start_x + half_child_width, this_start_y + child_height),
        Point(
            this_start_x + half_child_width + child_width,
            this_start_y + (child_height * 2),
        ),
    )
    south = Rect(
        Point(this_start_x + half_child_width, this_start_y),
        Point(
            this_start_x + half_child_width + child_width, this_start_y + child_height
        ),
    )
    west = Rect(
        Point(this_start_x, this_start_y + half_child_height),
        Point(
            this_start_x + child_width, this_start_y + half_child_height + child_height
        ),
    )
    east = Rect(
        Point(this_start_x + child_width, this_start_y + half_child_height),
        Point(
            this_start_x + (child_width * 2),
            this_start_y + half_child_height + child_height,
        ),
    )
    center = Rect(
        Point(this_start_x + half_child_width, this_start_y + half_child_height),
        Point(
            this_start_x + half_child_width + child_width,
            this_start_y + half_child_height + child_height,
        ),
    )
    return [north, south, west, east, center]


class QuadTreeSRC:
    def __init__(self, height: int, is_src: bool):
        self.max_domain = 2 ** height
        self.qdag_dict = QuadTreeSRC._build_quad_tree_src(height, is_src)
        self.is_src = is_src

    def find_containing_range_covers(self, point: Point) -> Set[Rect]:
        # Start at root:
        root_rect_list = self.qdag_dict[
            QDAG_ROOT
        ]  # Everything is a list, so just grab the first elt
        recursive_result = self._find_containing_range_covers_helper(
            root_rect_list[0], point
        )
        return set(root_rect_list).union(recursive_result)

    def _find_containing_range_covers_helper(
        self, rect: Rect, point: Point
    ) -> Set[Rect]:
        result = set()
        children_rect = self.qdag_dict[rect]
        for child in children_rect:
            if child.contains_point(point):
                # recur on containing child and add to overall result list
                subresult = self._find_containing_range_covers_helper(child, point)
                subresult.add(child)
                result.update(subresult)
        return result

    def get_single_range_cover(self, query: Rect) -> Rect:
        ### print("src:", query)
        query = Rect(query.start, Point(query.end_x() + 1, query.end_y() + 1))
        longest_side_length = max(query.x_length(), query.y_length())
        ### print("longest_side_length", longest_side_length)

        # Find the next highest power of 2 closest to the longest side length.
        # This is the side length of the range cover that we should pick (i.e.
        # the smallest range that covers the entire query):
        next_power_of_2 = 1
        while next_power_of_2 < longest_side_length:
            next_power_of_2 *= 2

        if next_power_of_2 == 1:
            p1 = query.start
            p2 = Point(query.end_x(), query.end_y())
            return Rect(p1, p2)

        # Find the lower-left point of the range cover by finding the nearest
        # multiple of (next_power_of_2 / 2):
        offset_multiple = next_power_of_2 // 2
        ### print("offset_multiple", offset_multiple)
        return self._get_single_range_cover_helper(
            query, next_power_of_2, offset_multiple
        )

    def _get_single_range_cover_helper(
        self, query: Rect, next_power_of_2: int, offset_multiple: int
    ) -> Rect:
        root_rect = self.qdag_dict[QDAG_ROOT][0]
        ### print("next_power_of_2", next_power_of_2)
        ### print("offset_multiple", offset_multiple)
        # This is integer division:
        cover_start_x = (
            math.floor(query.start_x() / float(offset_multiple)) * offset_multiple
        )
        cover_start_y = (
            math.floor(query.start_y() / float(offset_multiple)) * offset_multiple
        )
        cover_start = Point(cover_start_x, cover_start_y)
        ### print("cover_start", cover_start)

        cover_end_x = cover_start_x + next_power_of_2
        cover_end_y = cover_start_y + next_power_of_2
        cover_end = Point(cover_end_x, cover_end_y)
        ### print("cover_end", cover_end)

        result_rect = Rect(cover_start, cover_end)
        ### print("result_rect", result_rect)
        ### print("root_rect", root_rect)
        ### print("query", query)
        if result_rect in root_rect and query in result_rect:
            return result_rect

        # Otherwise, try to shift the rectangle the other way:
        cover_end_x = (
            math.ceil(query.end_x() / float(offset_multiple)) * offset_multiple
        )
        cover_end_y = (
            math.ceil(query.end_y() / float(offset_multiple)) * offset_multiple
        )
        cover_end = Point(cover_end_x, cover_end_y)
        ### print("cover_end", cover_end)

        cover_start_x = cover_end_x - next_power_of_2
        cover_start_y = cover_end_y - next_power_of_2
        cover_start = Point(cover_start_x, cover_start_y)
        ### print("cover_start", cover_start)

        result_rect = Rect(cover_start, cover_end)
        if result_rect in root_rect and query in result_rect:
            return result_rect
        else:
            return self._get_single_range_cover_helper(
                query, next_power_of_2 * 2, offset_multiple * 2
            )

    @classmethod
    def _build_quad_tree_src(cls, height: int, is_src: bool) -> Dict[Rect, List[Rect]]:
        root_rect = Rect(Point(0, 0), Point(2 ** height, 2 ** height))
        qdag = cls._build_quad_tree_src_helper(height, root_rect, is_src)
        qdag[QDAG_ROOT] = [root_rect]
        return qdag

    @classmethod
    def _build_quad_tree_src_helper(
        cls, height: int, bounding_box: Rect, is_src: bool
    ) -> Dict[Rect, List[Rect]]:
        if height <= 0:
            result = {}
            result[bounding_box] = []
            return result

        edge_dictionary = {}
        side_length = 2 ** height

        quad_divisions = get_quad_divisions(bounding_box)

        # If height >= 2, we need to make the in-between nodes for SRC:
        intermediate_divisions = []
        if is_src and height >= 2:
            intermediate_divisions = get_intermediate_divisions(bounding_box)

        child_rects = quad_divisions + intermediate_divisions

        main_dict = {}
        main_dict[bounding_box] = child_rects

        for child_rect in child_rects:
            child_dict = cls._build_quad_tree_src_helper(height - 1, child_rect, is_src)
            # Merge the two dicts together:
            main_dict.update(child_dict)

        return main_dict