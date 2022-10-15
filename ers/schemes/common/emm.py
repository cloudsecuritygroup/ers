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

from .emm_engine import EMMEngine

from typing import Set


class EMM:
    def __init__(self, emm_engine: EMMEngine):
        self.emm_engine = emm_engine

    def setup(self, security_parameter: int) -> bytes:
        return self.emm_engine.setup(security_parameter)

    def resolve(self, key: bytes, results: Set[bytes]) -> Set[bytes]:
        return self.emm_engine.resolve(key, results)
