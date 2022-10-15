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

from ...util.crypto import (
    SecureRandom,
    HashKDF,
    HMAC,
    Hash,
    SymmetricEncrypt,
    SymmetricDecrypt,
)

from typing import List, Dict, Set
from tqdm import tqdm

PURPOSE_HMAC = "hmac"
PURPOSE_ENCRYPT = "encryption"

DO_NOT_ENCRYPT = False


class EMMEngine:
    def __init__(self, max_x: int, max_y: int):
        self.MAX_X = max_x
        self.MAX_Y = max_y

    def setup(self, security_parameter: int) -> bytes:
        """
        Outputs secret key k.
        """
        return SecureRandom(security_parameter)

    def build_index(
        self, key: bytes, plaintext_mm: Dict[bytes, List[bytes]]
    ) -> Dict[bytes, bytes]:
        """
        Outputs an encrypted index I.
        """
        hmac_key = HashKDF(key, PURPOSE_HMAC)
        enc_key = HashKDF(key, PURPOSE_ENCRYPT)

        print("Encrypting with Pi_bas...")
        if not DO_NOT_ENCRYPT:
            encrypted_db = {}
            for label, values in tqdm(plaintext_mm.items()):
                token = HMAC(hmac_key, label)
                for index, value in enumerate(values):
                    ct_label = Hash(token + bytes(index))
                    ct_value = SymmetricEncrypt(enc_key, value)
                    encrypted_db[ct_label] = ct_value
            return encrypted_db
        else:
            print("WARNING: Not encrypting!")
            return {}

    def trapdoor(self, key: bytes, label: bytes) -> bytes:
        hmac_key = HashKDF(key, PURPOSE_HMAC)
        return HMAC(hmac_key, label)

    def search(
        self, search_token: bytes, encrypted_db: dict[bytes, bytes]
    ) -> Set[bytes]:
        results = set()

        # Iterate until can't find any more records:
        index = 0
        while True:
            ct_label = Hash(search_token + bytes(index))
            if ct_label in encrypted_db:
                data = encrypted_db[ct_label]
                if not isinstance(data, list):
                    data = [data]
                results.update(data)
            else:
                break
            index += 1

        return results

    def resolve(self, key: bytes, results: Set[bytes]) -> Set[bytes]:
        enc_key = HashKDF(key, PURPOSE_ENCRYPT)
        pt_values = set()
        for ct_value in results:
            pt_values.add(SymmetricDecrypt(enc_key, ct_value))
        return pt_values
