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
from ..structures.point_3d import Point3D

from typing import Dict, List, Set

from collections import defaultdict


class Linear3D(EMM):
    def __init__(self, emm_engine: EMMEngine, encrypted_db: Dict[bytes, bytes] = {}):
        self.encrypted_db = encrypted_db
        super().__init__(emm_engine)

    def build_index(self, key: bytes, plaintext_mm: Dict[Point3D, List[bytes]]) -> EMM:
        """
        Outputs an encrypted index using the Naive Linear scheme, where each file in
        the plaintext multimap is associated with the single point where the file lives.
        """
        modified_db = defaultdict(list)
        for point, files in plaintext_mm.items():
            modified_db[bytes(point)].extend(files)

        self.encrypted_db = self.emm_engine.build_index(key, modified_db)

    def trapdoor(self, key: bytes, p1: Point3D, p2: Point3D) -> Set[bytes]:
        trapdoors = set()

        for point in (
            Point3D(x, y,z) for x in range(p1.x, p2.x + 1) for y in range(p1.y, p2.y + 1) for z in range(p1.z, p2.z + 1)
        ):
            new_trp = self.emm_engine.trapdoor(key, bytes(point))
            trapdoors.add(new_trp)
        return trapdoors

    def search(self, trapdoors: Set[bytes]) -> Set[bytes]:
        results = set()
        for trpdr in trapdoors:
            result = self.emm_engine.search(trpdr, self.encrypted_db)
            results = results.union(result)
        return results


class Linear(EMM):
    def __init__(self, emm_engine: EMMEngine, encrypted_db: Dict[bytes, bytes] = {}):
        self.encrypted_db = encrypted_db
        super().__init__(emm_engine)

    def build_index(self, key: bytes, plaintext_mm: Dict[Point, List[bytes]]) -> EMM:
        """
        Outputs an encrypted index using the Naive Linear scheme, where each file in
        the plaintext multimap is associated with the single point where the file lives.
        """
        modified_db = defaultdict(list)
        for point, files in plaintext_mm.items():
            modified_db[bytes(point)].extend(files)

        self.encrypted_db = self.emm_engine.build_index(key, modified_db)

    def trapdoor(self, key: bytes, p1: Point, p2: Point) -> Set[bytes]:
        trapdoors = set()

        for point in (
            Point(x, y) for x in range(p1.x, p2.x + 1) for y in range(p1.y, p2.y + 1)
        ):
            new_trp = self.emm_engine.trapdoor(key, bytes(point))
            trapdoors.add(new_trp)
        return trapdoors

    def search(self, trapdoors: Set[bytes]) -> Set[bytes]:
        results = set()
        for trpdr in trapdoors:
            result = self.emm_engine.search(trpdr, self.encrypted_db)
            results = results.union(result)
        return results
