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

from ..structures.point import Point
from ..structures.rect import Rect
from ..structures.quad_tree_src import QuadTreeSRC
from .common.emm import EMM
from .common.emm_engine import EMMEngine

from typing import Dict, List

import math
import struct
from collections import defaultdict

class QdagSRC(EMM):
    def __init__(self, emm_engine: EMMEngine, encrypted_db: Dict[bytes, bytes] = {}):
        self.encrypted_db = encrypted_db
        self.qdag = None
        super().__init__(emm_engine)

    def build_index(self, key: bytes, plaintext_mm: Dict[Point, List[bytes]]):
        """
        Outputs an encrypted index I.
        """
        # Build QDAG over the domain space:
        x_nearest_height = math.ceil(math.log2(self.emm_engine.MAX_X))
        y_nearest_height = math.ceil(math.log2(self.emm_engine.MAX_Y))
        qdag_height = max(x_nearest_height, y_nearest_height)
        self.qdag = QuadTreeSRC(qdag_height, True)  # True for SRC

        # For every range query, insert them into the database at each of their
        # respective SRC ranges:
        modified_db = defaultdict(list)
        for point, files in plaintext_mm.items():
            # look up all queries which cover Point
            rects = self.qdag.find_containing_range_covers(point)
            # insert (query, file) for each file in files
            for file in files:
                for rect in rects:
                    serialized_query = self._convert_rect_to_bytes(rect)
                    modified_db[serialized_query].append(file)

        # Sigma.Setup over the modified_db:
        self.encrypted_db = self.emm_engine.build_index(key, modified_db)

    @classmethod
    def convert_query_to_bytes(self, p1: Point, p2: Point) -> bytes:
        return struct.pack("iiii", p1.x, p1.y, p2.x, p2.y)

    def _convert_rect_to_bytes(self, rect: Rect):
        """
        Converts a `Rect` to its serialized byte representation for storage in
        an encrypted DB.
        """
        return self.convert_query_to_bytes(rect.start, rect.end)

    def trapdoor(self, key: bytes, p1: Point, p2: Point) -> bytes:
        range_cover = self.qdag.get_single_range_cover(Rect(p1, p2))
        return self.emm_engine.trapdoor(
            key, self.convert_query_to_bytes(range_cover.start, range_cover.end)
        )

    def search(self, trapdoor):
        return self.emm_engine.search(trapdoor, self.encrypted_db)