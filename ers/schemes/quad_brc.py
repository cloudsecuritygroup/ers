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
from ..structures.quad_tree import QuadTree
from ..structures.rect import Rect

from typing import Dict, List, Set
from collections import defaultdict
from tqdm import tqdm
import itertools
import math
import struct



def next_power_of_2(x):
    return 1 if x == 0 else 2 ** (x - 1).bit_length()
class QuadBRC(EMM):
    def __init__(self, emm_engine: EMMEngine, encrypted_db: Dict[bytes, bytes] = {}):
        self.encrypted_db = encrypted_db
        self.qdag = None
        super().__init__(emm_engine)

    def build_index(self, key: bytes, plaintext_mm: Dict[Point, List[bytes]]):
        """
        Outputs an encrypted index I.
        """
        print("Build quadtree...")
        max_side_len = max(self.emm_engine.MAX_X, self.emm_engine.MAX_Y)
        start_level = math.ceil(math.log2(next_power_of_2(max_side_len)))
        self.qdag = QuadTree(
            Rect(Point(0, 0), Point(2 ** start_level-1, 2 ** start_level-1)),
            start_level
        )

        print("Inserting...")
        modified_db = defaultdict(list)
        for point, files in tqdm(plaintext_mm.items()):
            for rect_cover in self.qdag.find_containing_range_covers(point):
                #if point.x == 5 and point.y ==4:
                #    print(rect_cover)
                label_bytes = QuadBRC._convert_rect_to_bytes(rect_cover)
                modified_db[label_bytes].extend(files)

        # Sigma.Setup over the modified_db:
        self.encrypted_db = self.emm_engine.build_index(key, modified_db)

    @classmethod
    def convert_query_to_bytes(self, p1: Point, p2: Point) -> bytes:
        return struct.pack("iiii", p1.x, p1.y, p2.x, p2.y)

    @staticmethod
    def _convert_rect_to_bytes(rect: Rect):
        """
        Converts a `Rect` to its serialized byte representation for storage in
        an encrypted DB.
        """
        return QuadBRC.convert_query_to_bytes(rect.start, rect.end)

    def trapdoor(self, key: bytes, p1: Point, p2: Point) -> Set[bytes]:
        trapdoors = set()
        range_covers = self.qdag.get_brc_range_cover(Rect(p1, Point(p2.x, p2.y)))
        #print("Range Cover")
        #for i in range_covers:
        #    print(i)
        for rect_rc in range_covers:
            token_bytes = QuadBRC._convert_rect_to_bytes(rect_rc)
            new_trp = self.emm_engine.trapdoor(key, token_bytes)
            trapdoors.add(new_trp)
        return trapdoors

    def search(self, trapdoors: Set[bytes]) -> Set[bytes]:
        results = set()
        #print("results")
        for trpdr in trapdoors:
            result = self.emm_engine.search(trpdr, self.encrypted_db)
            #print(len(result))
            results = results.union(result)
        return results
