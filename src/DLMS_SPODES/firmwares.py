from functools import lru_cache
from typing import Optional
import pickle
import hashlib
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from .settings import settings


def init_cipher(key: bytes) -> tuple[Cipher, bytes]:
    """Initialize AES-CBC cipher with random IV"""
    iv = os.urandom(16)
    cipher = Cipher(
        algorithms.AES(key),
        modes.CBC(iv),
        backend=default_backend()
    )
    return cipher, iv


def decrypt(key: bytes, iv: bytes, ciphertext: bytes) -> bytes:
    """Decrypt data with hash verification: dec(dummy + data + sha256)"""
    cipher = Cipher(
        algorithms.AES(key),
        modes.CBC(iv),
        backend=default_backend()
    )
    decryptor = cipher.decryptor()
    # Decrypt and remove padding
    padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
    # Verify hash
    data, data_hash = plaintext[16:-32], plaintext[-32:]
    if hashlib.sha256(data).digest() == data_hash:
        return data
    else:
        raise ValueError('Invalid password or corrupted data')


def encrypt(key: bytes, iv: bytes, data: bytes) -> bytes:
    """Encrypt data with hash: ciphertext = enc(dummy + plaintext + sha256)"""
    # Prepare data (16 dummy bytes + data + hash)
    plaintext = bytes(16) + data + hashlib.sha256(data).digest()

    # Add padding
    padder = padding.PKCS7(128).padder()
    padded_plaintext = padder.update(plaintext) + padder.finalize()

    # Encrypt
    cipher = Cipher(
        algorithms.AES(key),
        modes.CBC(iv),
        backend=default_backend()
    )
    encryptor = cipher.encryptor()
    return encryptor.update(padded_plaintext) + encryptor.finalize()


@lru_cache(maxsize=10)
def get_firmware(man: bytes) -> Optional[tuple[
    dict[tuple[tuple[int, int, int], str], bytes],
    dict[tuple[int, str], bytes]
]]:
    for firmware in settings.firmwares:
        if firmware.man.encode() == man:
            match firmware.key.codec:
                case "ascii":
                    cipher_key = firmware.key.value.encode("ascii")
                case "hex":
                    cipher_key = bytes.fromhex(firmware.key.value)
                case _:
                    raise ValueError(f"in get firmware, unknown firmware.key.codec={firmware.key.codec}")
            new_firmwares = {}
            new_boots = {}
            with open(firmware.path, 'rb') as file:
                try:
                    name, firmwares_, boots_ = pickle.load(file)
                    load_name, version = name.split('_')

                    if load_name == "CryptoFirmware":
                        iv = os.urandom(16)
                        for it in firmwares_:
                            decryption = decrypt(cipher_key, iv, firmwares_[it])
                            new_firmwares[it] = decryption
                        for it in boots_:
                            decryption = decrypt(cipher_key, iv, boots_[it])
                            new_boots[it] = decryption
                    else:
                        raise ValueError(f"Wrong firmware.path={firmware.path}")
                except KeyError as e:
                    raise ValueError(f"Decoding error firmware.path={firmware.path}, {e}")
                except ValueError as e:
                    raise ValueError(f"Decoding error firmware.path={firmware.path}, {e}")
                except Exception as e:
                    raise ValueError(f"unknown error: {e}")
            return new_firmwares, new_boots
