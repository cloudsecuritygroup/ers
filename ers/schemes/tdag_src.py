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

from __future__ import annotations

from ..util.serialization import ObjectToBytes
from .common.emm_engine import EMMEngine
from .common.emm import EMM
from ..structures.point import Point
from ..structures.tdag import Tdag
from ..util.serialization import ObjectToBytes

from collections import defaultdict

from tqdm import tqdm
import collections

import math

class TdagSRC(EMM):
    def __init__(self, emm_engine: EMMEngine, encrypted_db: Dict[bytes, bytes] = {}):
        self.encrypted_db = encrypted_db
        self.level_x = None
        self.level_y = None
        super().__init__(emm_engine)

    @classmethod
    def descend_tree(self, val: int, rnge: List[int]) -> List[int]:
        rnges = []
        while rnge != [val, val]:
            if rnge not in rnges:
                rnges.append(rnge)

            middle = ((rnge[0] + rnge[1]) // 2)

            mid_0 = (middle  - ((rnge[0] + rnge[1]) // 4))
            mid_1 = (middle  + ((rnge[0] + rnge[1]) // 4))+1



            if val >= mid_0 and val <= mid_1 and (rnge[1] - rnge[0]) > 1:
                if [mid_0, mid_1] not in rnges:
                    rnges.append([mid_0, mid_1])
   
            if val <= ((rnge[0] + rnge[1]) // 2):
                rnge = [rnge[0], ((rnge[0] + rnge[1]) // 2)]
            else:
                rnge = [((rnge[0] + rnge[1]) // 2) + 1, rnge[1]]


        rnges.append([val, val])
        return rnges

    def build_index(self, key: bytes, plaintext_mm: Dict[Point, List[bytes]]) -> Dict[Tuple[int, int], int]:
        x_tree_height = math.ceil(math.log2(self.emm_engine.MAX_X))
        y_tree_height = math.ceil(math.log2(self.emm_engine.MAX_Y))

        self.x_tree = Tdag.initialize_tree(x_tree_height)
        self.y_tree = Tdag.initialize_tree(y_tree_height)

        self.level_x = x_tree_height
        self.level_y = y_tree_height

        modified_db = defaultdict(list)
        for point, vals in tqdm(plaintext_mm.items()):
            full_x_range = [0, self.emm_engine.MAX_X - 1]
            x_roots = TdagSRC.descend_tree(point.x, full_x_range)
            for root in x_roots:
                full_y_range = [0, self.emm_engine.MAX_Y - 1]
                y_path = TdagSRC.descend_tree(point.y, full_y_range)
                for y_node in y_path:
                    label = ObjectToBytes([root, y_node])
                    modified_db[label].extend(vals)

        self.encrypted_db = self.emm_engine.build_index(key, modified_db)


    def generate_cover(self, p1: Point, p2: Point):
        x_cover = self.x_tree.get_single_range_cover((p1.x, p2.x))
        y_cover = self.y_tree.get_single_range_cover((p1.y, p2.y))
        return (x_cover, y_cover)

    def trapdoor(self, key, p1: Point, p2: Point) -> List[Tuple[int, int]]:
        cover = self.generate_cover(p1, p2)
        return self.emm_engine.trapdoor(key, ObjectToBytes(cover))

    def search(self, trapdoor) -> ResolveDone:
        return self.emm_engine.search(trapdoor, self.encrypted_db)
