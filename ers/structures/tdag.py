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

from typing import List, Tuple

import functools


class Tdag:
    def __init__(self, left, right, mid, rng, height):
        self.left = left
        self.right = right
        self.middle = mid
        self.range = rng
        self.height = height


    def get_single_range_cover(self, query_range: Tuple[int, int]) -> Tuple[int, int]:
        q = self.get_single_range_cover_helper(query_range)
        return q

    def get_single_range_cover_helper(self, query_range: Tuple[int, int]) -> Tuple[int, int]:
        if self.interval_contains_interval(self.range, query_range):
            left = None
            right = None
            middle = None
            if self.middle and self.left and self.right:
                if self.interval_contains_interval(self.middle, query_range):
                    if (not self.interval_contains_interval(self.left.range, query_range)) and (not self.interval_contains_interval(self.right.range, query_range)):
                        return self.middle
            if self.left:
                left = self.left.get_single_range_cover_helper(query_range)
            if self.right:
                right = self.right.get_single_range_cover_helper(query_range)
            if left is None:
                if right is None:
                    return self.range
                else:
                    return right
            else:
                return left

        else:
            return None


    @classmethod
    def __init_tree(cls, height: int, left: int, right: int) -> "RangeTree":
        if height < 0:
            return None
        else:
            midpoint = ((right + left) // 2)

            mid_0 = midpoint  - ((right + left) // 4)
            mid_1 = midpoint  + ((right + left) // 4) +1

            return cls(
                cls.__init_tree(height - 1, left, left + int((right - left) / 2)),
                cls.__init_tree(height - 1, left + int((right - left) / 2) + 1, right),
                [mid_0, mid_1],
                (left, right),
                height,
            )

    @classmethod
    def initialize_tree(cls, height: int) -> "RangeTree":
        return cls.__init_tree(height, 0, pow(2, height) - 1)

    @classmethod
    def interval_contains_interval(
        cls, main: Tuple[int, int], secondary: Tuple[int, int]
    ) -> bool:
        return (main[0] <= secondary[0]) and (main[1] >= secondary[1])

