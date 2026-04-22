from functools import lru_cache
from typing import Optional
from enum import IntEnum
import pickle
import hashlib
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from COSEMpdu.x690 import Tag
from COSEMpdu.x680 import NamedType, EnumerationList, EnumerationMember, Class, TaggingMode
from COSEMpdu.x680.constrained_type import SizeConstraint
from COSEMpdu.ber import SequenceType, IntegerType, ChoiceType, create_alternatives, EnumeratedType, OctetStringType, ConstrainedOctetStringType, TaggedType
from .settings import settings


class TargetType_(IntEnum):
    Application = 1
    Bootloader = 2
    Ble = 3


type ImageInstance = int
type ImageData = bytes
type Version = tuple[int, int, int]
type FirmwareId = bytes
type Preinstall = Optional[TargetType_]
type Firmwares = dict[tuple[FirmwareId, TargetType_], tuple[ImageInstance, Preinstall, Version, ImageData]]


class TargetTypeList(EnumerationList):
    members = (
        EnumerationMember("application", 1),
        EnumerationMember("bootloader", 2),
        EnumerationMember("ble", 3)
    )


class TargetType(EnumeratedType):
    named_members = TargetTypeList()


class Version1(SequenceType):
    components = (
        NamedType("target", TargetType),
        NamedType("firmware-id", OctetStringType),
        NamedType("firmware-version", OctetStringType)
    )


class MetaData(ChoiceType):
    alternatives = create_alternatives(
        NamedType("version1", Version1)
    )


class MetaDataTagged(TaggedType[MetaData]):
    tag = Tag(0, class_=Class.CONTEXT_SPECIFIC)
    mode = TaggingMode.EXPLICIT


class OctetStringTypeSize4(ConstrainedOctetStringType):
    constraint_spec = SizeConstraint(4)
    value: OctetStringType


class FirmwareImagePackage(SequenceType):
    components = (
        NamedType("magic", IntegerType),
        NamedType("meta-data", MetaDataTagged),
        NamedType("firmware-data", OctetStringType),
        NamedType("crc", OctetStringTypeSize4),
    )

    @property
    def meta_data(self) -> MetaDataTagged:
        return self[1]


def init_cipher(key: bytes) -> tuple[Cipher[modes.CBC], bytes]:
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
