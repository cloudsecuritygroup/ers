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

from ..structures.point_3d import Point3D
from ..structures.rect_3d import Rect3D
from ..structures.quad_tree_3d import QuadTree3D
from .common.emm import EMM
from .common.emm_engine import EMMEngine
from ..util.serialization import ObjectToBytes


from typing import Dict, List

import math

from collections import defaultdict

import struct
from tqdm import tqdm


def next_power_of_2(x):
    return 1 if x == 0 else 2 ** (x - 1).bit_length()


class QuadBRC3D(EMM):
    def __init__(self, emm_engine: EMMEngine, encrypted_db: Dict[bytes, bytes] = {}):
        self.encrypted_db = encrypted_db
        self.quad = None
        super().__init__(emm_engine)

    def build_index(self, key: bytes, plaintext_mm: Dict[Point3D, List[bytes]]):
        """
        Outputs an encrypted index I.
        """
        print("Build quadtree...")
        max_side_len = max(self.emm_engine.MAX_X, self.emm_engine.MAX_Y)
        start_level = math.ceil(math.log2(next_power_of_2(max_side_len)))
        self.quad = QuadTree3D(
            Rect3D(Point3D(0, 0, 0), Point3D(2 ** start_level-1, 2 ** start_level-1,2 ** start_level-1)),
            start_level
        )

        print("Inserting...")
        modified_db = defaultdict(list)
        for point, files in tqdm(plaintext_mm.items()):
            for rect_cover in self.quad.find_containing_range_covers(point):
                #if point.x == 5 and point.y ==4:
                #    print(rect_cover)
                label_bytes = self._convert_rect_to_bytes(rect_cover)
                modified_db[label_bytes].extend(files)

        # Sigma.Setup over the modified_db:
        self.encrypted_db = self.emm_engine.build_index(key, modified_db)

    def _convert_rect_to_bytes(self, rect: Rect3D):
        """
        Converts a `Rect3D` to its serialized byte representation for storage in
        an encrypted DB.
        """
        return struct.pack(
            "iiiiii",
            rect.start.x,
            rect.start.y,
            rect.start.z,
            rect.end.x,
            rect.end.y,
            rect.end.z,
        )

    def trapdoor(self, key: bytes, p1: Point3D, p2: Point3D) -> bytes:
        range_covers = self.quad.get_brc_range_cover(Rect3D(p1, p2))

        trapdoors = set()

        for rect in range_covers:
            token_bytes = self._convert_rect_to_bytes(rect)
            new_trp = self.emm_engine.trapdoor(key, token_bytes)
            trapdoors.add(new_trp)
        return trapdoors

    def search(self, trapdoor):
        results = set()
        for trpdr in trapdoor:
            result = self.emm_engine.search(trpdr, self.encrypted_db)
            results = results.union(result)
        return results
