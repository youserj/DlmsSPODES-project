from enum import Enum


def version():
    return "0.1.0"


class Language(Enum):
    ENGLISH = 'English'
    RUSSIAN = 'Russian'


__current_language = Language.RUSSIAN


def set_current_language(value: str):
    global __current_language
    __current_language = Language(value)


def get_current_language() -> Language:
    return __current_language


def get_supporting_language() -> list[str]:
    return [language.name for language in Language]
