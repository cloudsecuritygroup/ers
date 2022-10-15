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


class RangeTree:
    def __init__(self, left, right, rng, height):
        self.left = left
        self.right = right
        self.range = rng
        self.height = height

    @functools.lru_cache(maxsize=None)
    def get_range_cover(self, query_range: Tuple[int, int]) -> List[Tuple[int, int]]:
        result = []

        # If self.range within interval, add it to the range; do not traverse
        if self.interval_contains_interval(query_range, self.range):
            return [(self.height, self.range)]
        else:
            result = []
            if self.left:
                left_res = self.left.get_range_cover(query_range)
                if len(left_res) > 0:
                    result.extend(left_res)
            if self.right:
                right_res = self.right.get_range_cover(query_range)
                if len(right_res) > 0:
                    result.extend(right_res)
            return result

    def get_single_range_cover(self, query_range: Tuple[int, int]) -> Tuple[int, int]:
        if self.interval_contains_interval(self.range, query_range):
            left = None
            right = None
            if self.left:
                left = self.left.get_single_range_cover(query_range)
            if self.right:
                right = self.right.get_single_range_cover(query_range)
            if left is None:
                if right is None:
                    return self.range
                else:
                    return right
            else:
                return left
        else:
            return None

    def get_brc_range_cover(
        self, query_range: Tuple[int, int]
    ) -> List[Tuple[int, int]]:
        range_cover = self.get_range_cover(query_range)
        return self.__remove_height_metadata(range_cover)

    def get_urc_range_cover(
        self, query_range: Tuple[int, int]
    ) -> List[Tuple[int, int]]:
        range_cover = self.get_range_cover(query_range)
        while not self.__satisfies_urc_condition(range_cover):
            for result in reversed(range_cover):
                if abs(result[1][1] - result[1][0]) > 0:
                    split = [
                        (
                            result[0] - 1,
                            tuple(
                                [
                                    result[1][0],
                                    result[1][0]
                                    + int((result[1][1] - result[1][0]) / 2),
                                ]
                            ),
                        ),
                        (
                            result[0] - 1,
                            tuple(
                                [
                                    result[1][0]
                                    + int((result[1][1] - result[1][0]) / 2)
                                    + 1,
                                    result[1][1],
                                ]
                            ),
                        ),
                    ]
                    range_cover.remove(result)
                    range_cover.extend(split)
                    break

        return self.__remove_height_metadata(range_cover)

    def __remove_height_metadata(self, range_cover):
        return list(map(lambda tup: tup[1], range_cover))

    def get_range_cover_bits(
        self, query_range: Tuple[int, int]
    ) -> List[Tuple[int, int]]:
        result = []

        # If self.range within interval, add it to the range; do not traverse
        if self.interval_contains_interval(query_range, self.range):
            return [[]]
        else:
            result = []
            if self.left:
                left_res = self.left.get_range_cover_bits(query_range)
                for r in left_res:
                    result.append([0] + r)
            if self.right:
                right_res = self.right.get_range_cover_bits(query_range)
                for r in right_res:
                    result.append([1] + r)
            return result

    def __str__(self):
        return (
            str(self.range)
            + "\n"
            + ("    " * self.height)
            + "L: "
            + str(self.left)
            + "\n"
            + ("    " * self.height)
            + "R: "
            + str(self.right)
        )

    @classmethod
    def __init_tree(cls, height: int, left: int, right: int) -> "RangeTree":
        if height < 0:
            return None
        else:
            return cls(
                cls.__init_tree(height - 1, left, left + int((right - left) / 2)),
                cls.__init_tree(height - 1, left + int((right - left) / 2) + 1, right),
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

    def __satisfies_urc_condition(self, results) -> bool:
        seen_levels = set()
        max_level = 0
        for result in results:
            if result[0] > max_level:
                max_level = result[0]
            seen_levels.add(result[0])

        for lvl in range(0, max_level + 1):
            if lvl not in seen_levels:
                return False
        return True
