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
from ..structures.point_3d import Point3D

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, hmac, serialization, constant_time
from cryptography.hazmat.primitives import padding as sym_padding
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

import random
import os
import math
import pprint
import functools


def check_type(arg, corr_type, param_name: str, func_name: str) -> None:
    """
    A helper function for argument type checking.
    """
    if not isinstance(arg, corr_type):
        print(f'\nParameter "{param_name}" to {func_name} must of type {corr_type}!')
        print(f"Instead, it is: {type(arg)}\n")
        raise TypeError


def Hash(data: bytes) -> bytes:
    """
    Computes a cryptographically secure hash of data.
    Params:
        > data - bytes

    Returns: the SHA512 hash of the input data (bytes)
    """
    digest = hashes.Hash(hashes.SHA512())
    digest.update(data)
    return digest.finalize()


def HMAC(key: bytes, data: bytes) -> bytes:
    """
    Compute a SHA-512 hash-based message authentication code (HMAC) of data.
    Returns an error if key is not 128 bits (16 bytes).

    You should use this function if you want a “keyed hash” instead of simply calling Hash
    on the concatenation of key and data, since in practical applications,
    doing a simple concatenation can allow the adversary to retrieve the full key.

    Params:
        > key  - bytes
        > data - bytes

    Returns: SHA-512 hash-based message authentication code (HMAC) of data (bytes)
    """
    h = hmac.HMAC(key, hashes.SHA512())
    h.update(data)
    return h.finalize()


def HMACEqual(hmac1: bytes, hmac2: bytes) -> bool:
    """
    Check if an HMAC is correct in constant time wrt the number of matching bytes.
    This is important to avoid timing attacks.

    Params:
        > hmac1 - bytes
        > hmac2 - bytes

    Returns: Boolean conditional on if hmacs match
    """
    return constant_time.bytes_eq(hmac1, hmac2)


def HashKDF(key: bytes, purpose: str) -> bytes:
    """
    Takes a key and a purpose and returns a new key.
    HashKDF is a keyed hash function that can generate multiple keys from a single key.
    This can simplify your key management schemes.

    Note that the "purpose" adds another input the the hash function such that the same password can produce
    more than one key.

    Params:
        > key - bytes
        > purpose - string

    Returns: new key (bytes)
    """

    check_type(key, bytes, "key", "HashKDF")
    check_type(purpose, str, "purpose", "HashKDF")

    hkdf = HKDF(
        algorithm=hashes.SHA512(),
        length=len(key),
        salt=None,
        info=purpose.encode(),
    )
    key = hkdf.derive(key)
    return key


def PasswordKDF(password: str, salt: bytes, keyLen: int) -> bytes:
    """
    Output some bytes that can be used as a symmetric key. The size of the output equals keyLen.
    A password-based key derivation function can be used to deterministically generate a cryptographic key
    from a password or passphrase.

    A password-based key derivation function is an appropriate way to derive a key from a password,
    if the password has at least a medium level of entropy (40 bits or so).

    Ideally, the salt should be different for each user or use of the function.
    Avoid using the same constant salt for everyone,
    as that may enable an attacker to create a single lookup table for reversing this function.

    Params:
        > password - string
        > salt - bytes
        > keyLen - int

    Returns: A key of length keyLen (bytes)
    """

    check_type(password, str, "password", "PasswordKDF")
    check_type(salt, bytes, "salt", "PasswordKDF")
    check_type(keyLen, int, "keyLen", "PasswordKDF")

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=keyLen,
        salt=salt,
        iterations=100000,
    )
    key = kdf.derive(password.encode())
    return key


def SymmetricEncrypt(key: bytes, plaintext: bytes) -> bytes:
    """
    Encrypt the plaintext using AES-CBC mode with the provided key and IV.
    Pads plaintext using 128 bit blocks. Requires a valid size key.
    The ciphertext at the end will inlcude the IV as the last 16 bytes.

    Params:
        > key - bytes (128 bits)
        > plaintext - bytes

    Returns: A ciphertext using AES-CBC mode with the provided key and IV (bytes)
    """
    padder = sym_padding.PKCS7(128).padder()
    padded_data = padder.update(plaintext)
    padded_data += padder.finalize()

    iv = SecureRandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    return ciphertext + iv


def SymmetricDecrypt(key: bytes, ciphertext: bytes) -> bytes:
    """
    Decrypt the ciphertext using the key. The last 16 bytes of the ciphertext should be the IV.

    Params:
        > key        - bytes
        > iv         - bytes
        > ciphertext - bytes

    Returns: A plaintext, decrypted from the given ciphertext, key and iv (bytes).
             If the padding in wrong after decryption (which will happen if the wrong key is used),
             then the decryption will be returned with the incorrect padding.
    """
    iv = ciphertext[-16:]
    ciphertext = ciphertext[:-16]

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    unpadder = sym_padding.PKCS7(128).unpadder()
    plaintext = unpadder.update(plaintext)
    plaintext += unpadder.finalize()

    return plaintext


def SecureRandom(num_bytes: int) -> bytes:
    """
    Given a length, return that many randomly generated bytes. Can be used for an IV or symmetric key.

    Params:
        > num_bytes - int

    Returns: num_bytes random bytes
    """

    check_type(num_bytes, int, "num_bytes", "SecureRandom")
    return os.urandom(num_bytes)
