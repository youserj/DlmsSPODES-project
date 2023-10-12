import logging
import os
import tomllib


print("Path: ", os.getcwd())

logger = logging.getLogger(__name__)
logger.level = logging.INFO


def get_values(*args: str) -> dict | None:
    args = list(args)
    par = config
    while args:
        key = args.pop(0)
        try:
            par = par[key]
            continue
        except KeyError as e:
            logger.info(e.args[0])
            return None
    return par


def get_values2(*args: str) -> tuple[str, int]:
    args2 = list(args)
    par = config
    while args2:
        key = args2.pop(0)
        try:
            par = par[key]
            continue
        except KeyError as e:
            logger.info(e.args[0])
            return ".".join(list(args)), -1
    return par, 0


try:
    with open("./config.toml", "rb") as f:
        config = tomllib.load(f)
except FileNotFoundError as e:
    logger.warning(e)
    config = None


_messages = get_values("DLMS", "messages")


def get_message(value: str) -> str:
    """translate %... from config.toml"""
    value: bytearray = bytearray(value, "utf-8")
    ret: bytearray = bytearray()
    while value:
        if value.startswith(b"$$"):
            value.pop(0)
            ret.append(value.pop(0))
        elif value.startswith(b"$"):
            key, sep, value = value[1:].partition(b"$")
            if key:
                if _messages and (translate := _messages.get(key.decode("utf-8"))):
                    val = bytes(translate, "utf-8")
                else:
                    val = key
                ret.extend(val)
        else:
            ret.append(value.pop(0))
    return ret.decode("utf-8", errors="strict")
