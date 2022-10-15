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


class QuadTree3D:
    def __init__(self, bounding_box: Rect3D, level: int):
        self.bounding_box = bounding_box
        self.level = level

    def get_brc_range_cover(self, query: Rect3D) -> List[Rect3D]:
        res = self._get_brc_range_cover_helper(query, self.bounding_box)
        return res

    def _get_brc_range_cover_helper(
        self, query: Rect3D, current_node: Rect3D
    ) -> List[Rect3D]:
        # If self.range within interval, add it to the range; do not traverse
        if query.contains_rect_inclusive(current_node):
            return [current_node]
        else:
            # Is there any possibility that current_node has children part of the query
            # range cover? (does current_node overlap query in any way?)
            if (
                current_node.end.x < query.start.x
                or current_node.end.y < query.start.y
                or current_node.end.z < query.start.z
                or query.end.x < current_node.start.x
                or query.end.y < current_node.start.y
                or query.end.z < current_node.start.z
            ):
                return []
            else:
                results = list()
                for child_rect in current_node.divide():
                    resp = self._get_brc_range_cover_helper(query, child_rect)
                    if resp not in results:
                        results.extend(resp)
                return results



    def find_containing_range_covers(self, point: Point3D) -> Set[Rect3D]:
            x, y, z = point.x, point.y, point.z
            for power in range(self.level+1):
                range_size = 2 ** power

                left_x = math.floor(x / range_size) * range_size
                left_y = math.floor(y / range_size) * range_size
                left_z = math.floor(z / range_size) * range_size
                right_x = left_x + range_size -1 
                right_y = left_y + range_size -1
                right_z = left_z + range_size -1

                yield Rect3D(Point3D(left_x, left_y, left_z), Point3D(right_x, right_y, right_z))



