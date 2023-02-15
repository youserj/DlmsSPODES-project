from __future__ import annotations
from typing import Dict, Type, Union
from abc import ABC, abstractmethod
from struct import pack


_services: Dict[int, Type[Union[AARE, ]]] = dict()
""" COSEM Services dictionary """


class Tag:
    """ APDU tag TODO: """
    value: int

    def __init__(self, value: int):
        self.value = value

    def __get__(self, instance, owner: COSEMPdu) -> int:
        return self.value

    def __set__(self, instance, value):
        raise ValueError("Tag no supported change")


class COSEMPdu(ABC):
    """ TODO: """
    tag: Tag

    def __init__(self, content: bytearray):
        if content.pop(0) != self.tag:
            raise ValueError(F'Wrong {self.__class__.__name__} tag, expected {self.tag}')
        length = content.pop(0)
        if len(content) != length:
            raise ValueError(F'Wrong PDU length, expected {length}, got {len(content)}')

    def __init_subclass__(cls, **kwargs):
        """ register subclass in _types with unique tag  """
        super().__init_subclass__(**kwargs)
        if hasattr(cls, 'tag'):
            _services.setdefault(cls.tag, cls)
        else:
            """ Handler for subclass without tag """

    @classmethod
    def from_content(cls, content: bytearray):
        tag = content[0]
        service = _services.get(tag, None)(content)
        if service is None:
            raise ValueError(F'service with tag:{tag} is absence in Service Dictionary')
        else:
            return service

    @property
    @abstractmethod
    def info(self) -> bytes:
        """ return info. All services, objects etc... TODO: """

    def content(self) -> bytes:
        return pack('BB', self.tag, len(self.info)) + self.info


class ACSE(COSEMPdu, ABC):
    """ TODO: """


class AARE(ACSE):
    """ TODO: """
    tag = Tag(61)

    def __init__(self, content: bytearray):
        super(AARE, self).__init__(content)

    @property
    def info(self) -> bytes:
        return bytes()


class AARQ(ACSE):
    """ TODO: """
    tag = Tag(60)

    def __init__(self, content: bytearray):
        super(AARQ, self).__init__(content)

    @property
    def info(self) -> bytes:
        return bytes()


if __name__ == '__main__':
    a = COSEMPdu.from_content(bytearray((61,3,1,2,4)))
    b = a.content().hex(' ')
    print(a)
