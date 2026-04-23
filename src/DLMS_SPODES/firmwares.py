from functools import lru_cache
from typing import IO, Optional
from StructResult.result import ValueOrError, Error
import pickle
import hashlib
import os
from semver import Version as SemVer
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from COSEMpdu.x690 import Tag
from COSEMpdu.x680.type import INTEGER, OCTET_STRING
from COSEMpdu.x680 import NamedType, EnumerationList, EnumerationMember, Class, TaggingMode
from COSEMpdu.x680.constrained_type import SizeConstraint
from COSEMpdu.ber import SequenceType, IntegerType, ChoiceType, create_alternatives, EnumeratedType, OctetStringType, ConstrainedOctetStringType, TaggedType
from .settings import settings


type ImageInstance = INTEGER
type ImageData = OCTET_STRING
type Version = tuple[INTEGER, INTEGER, INTEGER]
type FirmwareId = OCTET_STRING
type Firmwares = dict[tuple[FirmwareId, INTEGER], tuple[ImageInstance, Version, ImageData]]


class TargetTypeList(EnumerationList):
    members = (
        EnumerationMember("application", 1),
        EnumerationMember("bootloader", 2),
        EnumerationMember("ble", 3)
    )


class TargetType(EnumeratedType):
    named_members = TargetTypeList()
    application: INTEGER
    bootloader: INTEGER
    ble: INTEGER


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
    plaintext = bytes(16) + data + hashlib.sha256(data).digest()  # Prepare data (16 dummy bytes + data + hash)
    # Add padding
    padder = padding.PKCS7(128).padder()
    padded_plaintext = padder.update(plaintext) + padder.finalize()
    cipher = Cipher(
        algorithms.AES(key),
        modes.CBC(iv),
        backend=default_backend()
    )
    encryptor = cipher.encryptor()
    return encryptor.update(padded_plaintext) + encryptor.finalize()


GLOBAL_NAME = "CryptoFirmware"
VERSION = SemVer(1, 0, 1)


def io2firmwares(io: IO[bytes], key: bytes) -> ValueOrError[Firmwares]:
    res = {}
    try:
        name, firmwares = pickle.load(io)
        load_name, dat_version = name.split("_")
        if not SemVer.parse(dat_version).is_compatible(VERSION):
            return Error.from_e(ValueError(f"version of {io} not compatible with {VERSION}"))
        if load_name == GLOBAL_NAME:
            for key_, (instance, version, data) in firmwares.items():
                try:
                    plain = decrypt(key, os.urandom(16), data)
                except ValueError as e:
                    return Error.from_e(e, msg=F"error password: {key!r}")
                res[key_] = (instance, version, plain)
        else:
            return Error.from_e(FileExistsError(f"not correct {io}"))
    except KeyError as e:
        return Error.from_e(RuntimeError(f"decrypting error: {e}"))
    except Exception as e:
        return Error.from_e(e, msg="io2firmwres func error")
    return res


@lru_cache(maxsize=10)
def get_firmware(man: bytes) -> Optional[Firmwares]:
    for firmware in settings.firmwares:
        if firmware.man.encode() == man:
            match firmware.key.codec:
                case "ascii":
                    cipher_key = firmware.key.value.encode("ascii")
                case "hex":
                    cipher_key = bytes.fromhex(firmware.key.value)
                case _:
                    raise ValueError(f"in get firmware, unknown firmware.key.codec={firmware.key.codec}")
            with open(firmware.path, "rb") as file:
                if isinstance(res := io2firmwares(file, cipher_key), Error):
                    return None
                return res
    return None
