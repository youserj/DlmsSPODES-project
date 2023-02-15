from __future__ import annotations
from struct import pack


class AppVersion:
    __major: int
    __minor: int
    __patch: int
    __additional: str
    __match_args__ = ('major', 'minor', 'patch')

    def __init__(self, major: int, minor: int, patch: int, additional: str = ''):
        self.__major = major
        self.__minor = minor
        self.__patch = patch
        self.__additional = additional

    @classmethod
    def from_str(cls, value: str):
        match value.split(sep='.', maxsplit=2):
            case (major, minor, patch):
                match major.isdigit(), minor.isdigit(), patch.isdigit():
                    case True, True, True:                        return cls(int(major), int(minor), int(patch))
                    case True, True, False:
                        patch_seq = bytearray(patch, 'utf-8')
                        patch_seq.insert(0, ord('0'))  # if not founded integer when patch default value is 0
                        digit_pos = 0
                        while patch_seq[:digit_pos + 1].isdigit() and digit_pos < len(patch_seq):
                            digit_pos += 1
                        return cls(int(major), int(minor), int(patch_seq[:digit_pos]), patch_seq[digit_pos:].decode())
                    case _:                                      return cls(0, 0, 0)
            case _:                                              return cls(0, 0, 0)

    @property
    def major(self) -> int:
        return self.__major

    @property
    def minor(self) -> int:
        return self.__minor

    @property
    def patch(self) -> int:
        return self.__patch

    @property
    def additional(self) -> str:
        return self.__additional

    def __eq__(self, other: AppVersion):
        return hash(self) == hash(other) and self.__additional == other.additional

    def __gt__(self, other: AppVersion):
        return hash(self) > hash(other)

    def __ge__(self, other: AppVersion):
        return hash(self) >= hash(other)

    def __str__(self) -> str:
        return F'{self.__major}.{self.__minor}.{self.__patch}{F" <{self.__additional}>" if len(self.__additional) != 0 else ""}'

    def __hash__(self):
        """ to int6 every 2 byte for major, minor, patch """
        return self.__major * 0x10000_0000 + self.__minor * 0x10000 + self.__patch

    def select_nearest(self, variants: list[AppVersion | str]) -> AppVersion | None:
        """ select left nearest from list. If version is absence return None """
        app_versions: list[AppVersion | None] = [self]
        for version in variants:
            match version:
                case AppVersion(): app_versions.append(version)
                case str():        app_versions.append(self.from_str(version))
                case _:            pass
        app_versions.sort()
        app_versions.append(None)
        return app_versions[app_versions.index(self)-1]


if __name__ == '__main__':
    from time import perf_counter
    a = AppVersion.from_str('1.1.9d1')
    b = AppVersion(3,3,7)
    c = AppVersion(1,3,6)
    d = [a,b,c]
    d1 = sorted(d)
    print(a == b)
    print(b > a)
    match b:
        case AppVersion(3,3, patch) if patch<5:
            print('ok')
