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

import json
import base64

def _print_bytes(b: bytes) -> None:
    """
    A helper function to print bytes as base64.
    """
    print(base64.b64encode(b).decode("utf-8"))


def __bytes_to_b64(b: bytes) -> str:
    """
    A helper function that gives a base64 string representation of bytes.
    You probably do not need to use this directly.
    """
    return base64.b64encode(b).decode()


def __b64_to_bytes(b64: str) -> bytes:
    """
    A helper function that returns the bytes given by base64 string.
    You probably do not need to use this directly.
    """
    return base64.b64decode(b64)


def __detect_tags(s: str):
    return s[:3] == "^^^" and s[-3:] == "$$$"


    

def _prepare_bytes(o):
    """
    A helper funtion for ObjectToBytes
    """
    if isinstance(o, dict):
        result = {}
        for key, value in o.items():
            if isinstance(key, bytes):

                key = "^^^" + __bytes_to_b64(key) + "$$$"
            if isinstance(value, bytes):
                value = "^^^" + __bytes_to_b64(value) + "$$$"
            elif isinstance(value, dict) or isinstance(value, list):
                value = _prepare_bytes(value)
            result[key] = value
        return result

    if isinstance(o, list):
        result = []
        for item in o:
            if isinstance(item, bytes):
                item = "^^^" + __bytes_to_b64(item) + "$$$"
            elif isinstance(item, dict) or isinstance(item, list):
                item = _prepare_bytes(item)
            result.append(item)
        return result

    if isinstance(o, bytes):
        return "^^^" + __bytes_to_b64(o) + "$$$"

    elif isinstance(o, (int, str, float, bool)) or o is None:
        return o
    else:
        print(
            f"ERROR: Unserializable type {type(o)} detected! Valid types are [dict, list, int, str, float, bool, NoneType]"
        )
        raise ValueError




def _repair_bytes(o):
    """
    A helper funtion for ObjectToBytes
    """
    if isinstance(o, dict):
        result = {}
        for key, value in o.items():
            if isinstance(key, str):
                if __detect_tags(key):
                    key = __b64_to_bytes(key[3:-3])
            if isinstance(value, str):
                if __detect_tags(value):
                    value = __b64_to_bytes(value[3:-3])

            elif isinstance(value, dict) or isinstance(value, list):
                value = _repair_bytes(value)
            result[key] = value
        return result

    if isinstance(o, list):
        result = []
        for item in o:
            if isinstance(item, str):
                if __detect_tags(item):
                    item = __b64_to_bytes(item[3:-3])
            elif isinstance(item, dict) or isinstance(item, list):
                item = _repair_bytes(item)
            result.append(item)
        return result

    if isinstance(o, str):
        if __detect_tags(o):
            return __b64_to_bytes(o[3:-3])
        else:
            return o

    elif isinstance(o, (int, str, float, bool)) or o is None:
        return o
    else:
        print(
            f"ERROR: Undeserializable type {type(o)} detected! Valid types are [dict, list, int, str, float, bool, NoneType]"
        )
        raise ValueError




def ObjectToBytes(o: object) -> bytes:
    """
    A helper function that will serialize objects to bytes using JSON.
    It can serialize arbitrary nestings of lists and dictionaries containing ints, floats, booleans, strs, Nones, and bytes.

    A note on bytes and strings:
    This function encodes all bytes as base64 strings in order to be json compliant.
    The complimentary function, BytesToObject, will decode everything it detects to be a base64 string
    back to bytes. If you store a base64 formatted string, it would also be decoded to bytes.

    To alleviate this, the base64 string are prefixed with "^^^" and suffixed with "$$$", and the function
    checks for those tags instead.

    In the (unlikely) event you store a string with this format it will be decoded to bytes!
    """
    if isinstance(o, tuple):
        o = list(o)
    o = _prepare_bytes(o)
    return json.dumps(o).encode()


def BytesToObject(b: bytes) -> object:
    """
    A helper function that will deserialize bytes to an object using JSON. See caveats in ObjectToBytes().
    """
    obj = json.loads(b.decode())
    return _repair_bytes(obj)
