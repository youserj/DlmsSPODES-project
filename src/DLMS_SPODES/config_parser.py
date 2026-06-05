import os
import sys
import tomllib
from typing_extensions import deprecated


print("Path: ", os.getcwd())


@deprecated("use settings.settings")
def get_values(*args: str) -> dict | None:
    args = list(args)
    par = config
    while args:
        key = args.pop(0)
        try:
            par = par[key]
            continue
        except KeyError as e:
            print(f"error: {e.args[0]}")
            return None
    return par



if getattr(sys, "frozen", False):
    print("PyInstaller builden")
    path = os.path.join(os.path.dirname(sys.executable), 'config.toml')
    if not os.path.isfile(path):
        base_path = sys._MEIPASS
        print(f"fallback to _MEIPASS: {base_path}")
        path = os.path.join(base_path, 'config.toml')
        print(f"_MEIPASS path: {path}")
else:
    path = os.path.join(os.path.dirname(__file__), "config.toml")
    if not os.path.isfile(path):
        path = ".//config.toml"
if not os.path.isfile(path):
    print("NOT FIND CONFIGURATION: <config.toml>")
    sys.exit(1)
with open(path, "rb") as f:
    config = tomllib.load(f)
    print(F"Find configuration <config.toml> with path: {f}")

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
