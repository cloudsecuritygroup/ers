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

from .rect_3d import Rect3D
from .point_3d import Point3D

from typing import Dict, List, Set

import math

QDAG_ROOT = "__root__"


class QuadTreeSRC3D:
    def __init__(self, height: int, is_src: bool):
        self.max_domain = 2 ** height
        self.qdag_dict = QuadTreeSRC3D._build_quad_tree_src(height, is_src)
        self.is_src = is_src

    def find_containing_range_covers(self, point: Point3D) -> Set[Rect3D]:
        # Start at root:
        root_rect_list = self.qdag_dict[
            QDAG_ROOT
        ]  # Everything is a list, so just grab the first elt
        recursive_result = self._find_containing_range_covers_helper(
            root_rect_list[0], point
        )
        return set(root_rect_list).union(recursive_result)

    def _find_containing_range_covers_helper(
        self, rect: Rect3D, point: Point3D
    ) -> Set[Rect3D]:
        result = set()
        children_rect = self.qdag_dict[rect]
        #print(rect, ":", children_rect)
        for child in children_rect:
            if child.contains_point(point):
                # recur on containing child and add to overall result list
                subresult = self._find_containing_range_covers_helper(child, point)
                subresult.add(child)
                result.update(subresult)
        return result

    def get_single_range_cover(self, query: Rect3D) -> Rect3D:
        ### print("src:", query)
        query = Rect3D(
            query.start,
            Point3D(query.end_x() + 1, query.end_y() + 1, query.end_z() + 1),
        )
        longest_side_length = max(query.x_length(), query.y_length(), query.z_length())
        ### print("longest_side_length", longest_side_length)

        # Find the next highest power of 2 closest to the longest side length.
        # This is the side length of the range cover that we should pick (i.e.
        # the smallest range that covers the entire query):
        next_power_of_2 = 1
        while next_power_of_2 < longest_side_length:
            next_power_of_2 *= 2

        if next_power_of_2 == 1:
            p1 = query.start
            p2 = Point3D(query.end_x(), query.end_y(), query.end_z())
            return Rect3D(p1, p2)

        # Find the lower-left point of the range cover by finding the nearest
        # multiple of (next_power_of_2 / 2):
        offset_multiple = next_power_of_2 // 2
        ### print("offset_multiple", offset_multiple)
        return self._get_single_range_cover_helper(
            query, next_power_of_2, offset_multiple
        )


    def _get_single_range_cover_helper(
        self, query: Rect3D, next_power_of_2: int, offset_multiple: int
    ) -> Rect3D:
        root_rect = self.qdag_dict[QDAG_ROOT][0]
        # print("next_power_of_2", next_power_of_2)
        # print("offset_multiple", offset_multiple)

        # This is integer division:
        left_cover_start_x = (
            math.floor(query.start_x() / float(offset_multiple)) * offset_multiple
        )
        left_cover_start_y = (
            math.floor(query.start_y() / float(offset_multiple)) * offset_multiple
        )
        left_cover_start_z = (
            math.floor(query.start_z() / float(offset_multiple)) * offset_multiple
        )

        left_cover_end_x = left_cover_start_x + next_power_of_2
        left_cover_end_y = left_cover_start_y + next_power_of_2
        left_cover_end_z = left_cover_start_z + next_power_of_2

        # Otherwise, try to shift the rectangle the other way:
        right_cover_end_x = (
            math.ceil(query.end_x() / float(offset_multiple)) * offset_multiple
        )
        right_cover_end_y = (
            math.ceil(query.end_y() / float(offset_multiple)) * offset_multiple
        )
        right_cover_end_z = (
            math.ceil(query.end_z() / float(offset_multiple)) * offset_multiple
        )

        right_cover_start_x = right_cover_end_x - next_power_of_2
        right_cover_start_y = right_cover_end_y - next_power_of_2
        right_cover_start_z = right_cover_end_z - next_power_of_2

        x_covers = [
            (left_cover_start_x, left_cover_end_x),
            (right_cover_start_x, right_cover_end_x),
        ]
        y_covers = [
            (left_cover_start_y, left_cover_end_y),
            (right_cover_start_y, right_cover_end_y),
        ]
        z_covers = [
            (left_cover_start_z, left_cover_end_z),
            (right_cover_start_z, right_cover_end_z),
        ]
        for start_x, end_x in x_covers:
            for start_y, end_y in y_covers:
                for start_z, end_z in z_covers:
                    cover_start = Point3D(start_x, start_y, start_z)
                    cover_end = Point3D(end_x, end_y, end_z)
                    result_rect = Rect3D(cover_start, cover_end)
                    if result_rect in root_rect and query in result_rect:
                        return result_rect

        return self._get_single_range_cover_helper(
            query, next_power_of_2 * 2, offset_multiple * 2
        )

    @classmethod
    def _build_quad_tree_src(
        cls, height: int, is_src: bool
    ) -> Dict[Rect3D, List[Rect3D]]:
        root_rect = Rect3D(
            Point3D(0, 0, 0), Point3D(2 ** height, 2 ** height, 2 ** height)
        )
        qdag = cls._build_quad_tree_src_helper(height, root_rect, is_src)
        qdag[QDAG_ROOT] = [root_rect]
        return qdag

    @classmethod
    def _build_quad_tree_src_helper(
        cls, height: int, bounding_box: Rect3D, is_src: bool
    ) -> Dict[Rect3D, List[Rect3D]]:
        if height <= 0:
            result = {}
            result[bounding_box] = []
            return result

        edge_dictionary = {}
        side_length = 2 ** height

        # If height >= 2, we need to make the in-between nodes for SRC:
        child_rects = []
        if height >= 2:
            child_rects = get_all_child_nodes_in_rect3d(bounding_box)
        else:
            child_rects = get_child_nodes_in_rect3d(bounding_box)

        if not is_src:
            child_rects = get_child_nodes_in_rect3d(bounding_box)


        main_dict = {}
        main_dict[bounding_box] = child_rects

        for child_rect in child_rects:
            child_dict = cls._build_quad_tree_src_helper(height - 1, child_rect, is_src)
            # Merge the two dicts together:
            main_dict.update(child_dict)

        return main_dict


def get_all_child_nodes_in_rect3d(rect: Rect3D) -> List[Rect3D]:
    """
    Returns the 27 direct and indirect QDAG nodes in 3-dimensions.
    """
    this_start_x = rect.start_x()
    this_start_y = rect.start_y()
    this_start_z = rect.start_z()

    this_width = rect.x_length()
    this_height = rect.y_length()
    this_depth = rect.z_length()

    child_width = this_width // 2
    child_height = this_height // 2
    child_depth = this_depth // 2

    half_child_width = child_width // 2
    half_child_height = child_height // 2
    half_child_depth = child_depth // 2

    rects = []
    for child_start_x in range(
        this_start_x, this_start_x + half_child_width * 3, half_child_width
    ):
        for child_start_y in range(
            this_start_y, this_start_y + half_child_height * 3, half_child_height
        ):
            for child_start_z in range(
                this_start_z, this_start_z + half_child_depth * 3, half_child_depth
            ):
                start_point = Point3D(child_start_x, child_start_y, child_start_z)
                end_point = Point3D(
                    child_start_x + child_width,
                    child_start_y + child_height,
                    child_start_z + child_depth,
                )
                rect = Rect3D(start_point, end_point)
                rects.append(rect)

    return rects


def get_child_nodes_in_rect3d(rect: Rect3D) -> List[Rect3D]:
    """
    Returns the 8 quad tree divisions in 3-dimensions.
    """
    this_start_x = rect.start_x()
    this_start_y = rect.start_y()
    this_start_z = rect.start_z()
    this_width = rect.x_length()
    this_height = rect.y_length()
    this_depth = rect.z_length()

    child_width = this_width // 2
    child_height = this_height // 2
    child_depth = this_depth // 2

    rects = []
    for child_start_x in [this_start_x, this_start_x + child_width]:
        for child_start_y in [this_start_y, this_start_y + child_height]:
            for child_start_z in [this_start_z, this_start_z + child_depth]:
                start_point = Point3D(child_start_x, child_start_y, child_start_z)
                end_point = Point3D(
                    child_start_x + child_width,
                    child_start_y + child_height,
                    child_start_z + child_depth,
                )
                rects.append(Rect3D(start_point, end_point))

    return rects
