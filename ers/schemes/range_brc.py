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

from .common.emm_engine import EMMEngine
from .common.emm import EMM
from ..structures.point import Point
from ..structures.range_tree import RangeTree
from ..util.serialization import ObjectToBytes

from typing import Dict, List, Set

import itertools
import math

from collections import defaultdict

from tqdm import tqdm


class RangeBRC(EMM):
    def __init__(self, emm_engine: EMMEngine, encrypted_db: Dict[bytes, bytes] = {}):
        self.encrypted_db = encrypted_db
        self.x_tree = None
        self.y_tree = None
        super().__init__(emm_engine)

    @classmethod
    def descend_tree(self, val: int, rnge: List[int]) -> List[int]:
        rnges = []
        while rnge != [val, val]:
            rnges.append(rnge)
            if val <= ((rnge[0] + rnge[1]) // 2):
                rnge = [rnge[0], ((rnge[0] + rnge[1]) // 2)]
            else:
                rnge = [((rnge[0] + rnge[1]) // 2) + 1, rnge[1]]

        rnges.append([val, val])
        return rnges

    def build_index(self, key: bytes, plaintext_mm: Dict[Point, List[bytes]]) -> EMM:
        x_tree_height = math.ceil(math.log2(self.emm_engine.MAX_X))
        y_tree_height = math.ceil(math.log2(self.emm_engine.MAX_Y))

        self.x_tree = RangeTree.initialize_tree(x_tree_height)
        self.y_tree = RangeTree.initialize_tree(y_tree_height)

        modified_db = defaultdict(list)
        for point, vals in tqdm(plaintext_mm.items()):
            full_x_range = [0, self.emm_engine.MAX_X - 1]
            x_roots = RangeBRC.descend_tree(point.x, full_x_range)
            for root in x_roots:
                full_y_range = [0, self.emm_engine.MAX_Y - 1]
                y_path = RangeBRC.descend_tree(point.y, full_y_range)
                for y_node in y_path:
                    label = ObjectToBytes([root, y_node])
                    modified_db[label].extend(vals)

        self.encrypted_db = self.emm_engine.build_index(key, modified_db)

    def generate_cover(self, p1: Point, p2: Point) -> Set[bytes]:
        x_covers = self.x_tree.get_brc_range_cover((p1.x, p2.x))
        y_covers = self.y_tree.get_brc_range_cover((p1.y, p2.y))
        return itertools.product(x_covers, y_covers)

    def trapdoor(self, key: bytes, p1: Point, p2: Point) -> Set[bytes]:
        trapdoors = set()

        for p1, p2 in self.generate_cover(p1, p2):
            token_bytes = ObjectToBytes([p1, p2])
            new_trp = self.emm_engine.trapdoor(key, token_bytes)
            trapdoors.add(new_trp)
        return trapdoors

    def search(self, trapdoors: Set[bytes]) -> Set[bytes]:
        results = set()
        for trpdr in trapdoors:
            result = self.emm_engine.search(trpdr, self.encrypted_db)
            results = results.union(result)
        return results
