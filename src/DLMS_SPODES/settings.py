import os
from pydantic import BaseModel, Field
import tomllib
from enum import Enum


class _ReportStruct(BaseModel):
    """
    Patterns. Use for function get_obj_report. Only for struct. Generate custom struct report instead standart. Where %nxx: n - name of struct element,
    xx - index of struct element; %vxx: v - value of struct element, xx - index of struct element
    """
    DayProfileAction: str = "%n00: %v00 - Тариф: %v02"


class _Report(BaseModel):
    empty: str = "--"
    empty_unit: str = "??"
    scaler_format: str = "{:.3f}"
    struct: _ReportStruct = Field(default_factory=_ReportStruct)


class _Collection(BaseModel):
    path: str = "./Types/"


class _FirmwaresKey(BaseModel):
    codec: str = "ascii"
    value: str = "00000000password"


class _Firmware(BaseModel):
    key: _FirmwaresKey = Field(default_factory=_FirmwaresKey)
    man: str = "KPZ"
    path: str = "./Firmwares/firmwares.dat"


class Settings(BaseModel):
    collection: _Collection = Field(default_factory=_Collection)
    report: _Report = Field(default_factory=_Report)
    firmwares: list[_Firmware] = Field(default_factory=list)


if not os.path.isfile(path := ".//config.toml"):
    path = F"{os.path.dirname(__file__)}{path}"
elif os.path.isfile(path):
    with open(path, "rb") as f:
        toml_data = tomllib.load(f)
        data = toml_data.get("DLMS", {})
        print(f"Find configuration <config.toml> with path: {f}")
        settings = Settings(**data)
else:
    print("NOT FIND CONFIGURATION: <config.toml>")
    toml_data = {}
    settings = Settings()


# remove in future


def version():
    return "0.2.0"


class Language(Enum):
    ENGLISH = 'English'
    RUSSIAN = 'Russian'


__current_language = Language.RUSSIAN


def set_current_language(value: str):
    global __current_language
    __current_language = Language(value)


def get_current_language() -> Language:
    return __current_language
