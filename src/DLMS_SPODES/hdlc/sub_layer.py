from struct import pack
from functools import cached_property


class LLC:
    __DESTINATION__LSAP: int = 0xe6
    __BROADCAST: int = 0xff
    __COMMAND: int = 0xe6
    __RESPONSE: int = 0xe7
    __QUALITY: int = 0x00
    __destination_lsap: int
    __source_lsap: int
    __info: bytes

    def __init__(self, content: bytearray = None,
                 message: bytes = None):
        if message is None:
            self.__destination_lsap = content.pop(0)
            if self.__destination_lsap not in (self.__DESTINATION__LSAP, self.__BROADCAST):
                raise ValueError(F'Destination tag wrong, expected {hex(self.__DESTINATION__LSAP), hex(self.__BROADCAST)}, got {hex(self.__destination_lsap)}')
            else:
                self.__source_lsap = content.pop(0)
                if self.__source_lsap not in (self.__COMMAND, self.__RESPONSE):
                    raise ValueError(F'Destination tag wrong, expected {hex(self.__COMMAND)}, {hex(self.__RESPONSE)}, got {hex(self.__source_lsap)}')
                else:
                    quality = content.pop(0)
                    if quality != self.__QUALITY:
                        raise ValueError(F'Quality tag wrong, expected {hex(self.__QUALITY)}, got {hex(quality)}')
                    else:
                        self.__info = bytes(content)
        else:
            self.__destination_lsap = self.__DESTINATION__LSAP
            self.__source_lsap = self.__COMMAND
            self.__info = message

    @property
    def info(self) -> bytes:
        return self.__info

    @cached_property
    def content(self) -> bytes:
        return pack('BBB', self.__destination_lsap, self.__source_lsap, self.__QUALITY) + self.__info

    def __str__(self):
        return F'{"broadcast " if self.__destination_lsap == self.__BROADCAST else ""}' \
               F'{"command" if self.__source_lsap == self.__COMMAND else "response"} {self.__info[:10].hex(" ")}'

    def __len__(self):
        return len(self.content)


if __name__ == '__main__':
    l = LLC(content=bytearray((0xe6, 0xe7, 0, 1, 2, 3)))
    print(l)
