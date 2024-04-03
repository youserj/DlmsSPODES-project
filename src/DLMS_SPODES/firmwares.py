from functools import lru_cache
import pickle
import hashlib
from Cryptodome.Util.Padding import pad, unpad
from Cryptodome.Random import get_random_bytes
from Cryptodome.Cipher import AES
from .config_parser import get_values


def init_cipher(key: bytes) -> AES:
    iv = get_random_bytes(16)
    return AES.new(key, AES.MODE_CBC, iv)


def decrypt(cipher: AES, ciphertext: bytes) -> bytes:
    """ decrypt data with it hash: dec(dummy + data + sha256) """
    plaintext = unpad(cipher.decrypt(ciphertext), 16)
    data, data_hash = plaintext[16: -32], plaintext[-32:]
    if hashlib.sha256(data).digest() == data_hash:
        return data
    else:
        raise KeyError(F'password is wrong')


def encrypt(cipher: AES, data: bytes) -> bytes:
    """ encrypt data with it hash: ciphertext = enc(dummy + plaintext + sha256) """
    plaintext = bytes(16) + data + hashlib.sha256(data).digest()
    return cipher.encrypt(pad(plaintext, 16))


@lru_cache(maxsize=10)
def get_firmware(man: bytes) -> tuple[dict, dict] | None:
    if firmwares := get_values("DLMS", "firmwares"):
        for f in firmwares:
            if f['man'].encode() == man:
                key_struct = f['key']
                value: str = key_struct['value']
                codec: str = key_struct['codec']
                match codec:
                    case "ascii":
                        cipher_key = value.encode("ascii")
                    case "hex":
                        cipher_key = bytes.fromhex(value)
                    case _:
                        raise ValueError(F"in get firmware, unknown {codec=}")
                new_firmwares: dict[tuple[tuple[int, int, int], str], bytes] = dict()
                new_boots: dict[tuple[int, str], bytes] = dict()
                cipher = init_cipher(cipher_key)
                with open((path := f["path"]), 'rb') as file:
                    try:
                        name, firmwares_, boots_ = pickle.load(file)
                        load_name, version = name.split('_')
                        if load_name == "CryptoFirmware":
                            for it in firmwares_:
                                decryption = decrypt(cipher, firmwares_[it])
                                new_firmwares[it] = decryption
                            for it in boots_:
                                decryption = decrypt(cipher, boots_[it])
                                new_boots[it] = decryption
                        else:
                            raise ValueError(F"Wrong {path=}")
                    except KeyError as e:
                        raise ValueError(F"Decoding error {path=}, {e}")
                    except ValueError as e:
                        raise ValueError(F"Decoding error {path=}, {e}")
                    except Exception as e:
                        raise ValueError(F"unknown error: {e}")
                return new_firmwares, new_boots
