from ..types import common_data_types as cdt
import datetime


class LogicalName(cdt.OctetString):
    """ Logical Name type. Default is CLock#1 """
    __match_args__ = ('a', 'b', 'c', 'd', 'e', 'f')
    NAME = F'{cdt.tn.OCTET_STRING}[6]'
    DEFAULT = b'\x00\x00\x01\x00\x00\xff'

    def validation(self):
        if len(self.contents) != 0x06:
            raise ValueError(F'Length of {self.__class__.__name__} must be 6, but got {len(self.contents)}: {self.contents.hex()}')

    def from_str(self, value: str) -> bytes:
        """ create logical_name: octet_string from string type ddd.ddd.ddd.ddd.ddd.ddd, ex.: 0.0.1.0.0.255 """
        raw_value = bytes()
        for typecast, separator in zip((self.__from_group_A, )*5+(self.__from_group_F, ), ('.', '.', '.', '.', '.', ' ')):
            try:
                element, value = value.split(separator, 1)
            except ValueError:
                element, value = value, ''
            raw_value += typecast(element)
        return raw_value

    def __from_group_A(self, value: str) -> bytes:
        if isinstance(value, str):
            if value == '':
                return b'\x00'
            try:
                return int(value).to_bytes(1, 'big')
            except OverflowError:
                raise ValueError(F'Int too big to convert {value}')
        else:
            raise TypeError(F'Unsupported type validation from string, got {value.__class__}')

    def __from_group_F(self, value: str) -> bytes:
        if isinstance(value, str):
            if value == '':
                return b'\xff'
            try:
                return int(value).to_bytes(1, 'big')
            except OverflowError:
                raise ValueError(F'Int too big to convert {value}')
        else:
            raise TypeError(F'Unsupported type validation from string, got {value.__class__}')

    def __str__(self):
        return '.'.join(map(str, self.contents))

    def validate_from(self, value: str, cursor_position=None) -> tuple[str, int]:
        try:
            possible = type(self)(value)
            return value, cursor_position  # TODO: wrong position ???
        except ValueError:
            with_separator = F'{value[:-1]}.{value[-1]}'
            type(self)(with_separator)  # check possible
            return with_separator, cursor_position

    def __hash__(self):
        return int.from_bytes(self.contents, 'big')

    @property
    def a(self) -> int:
        """ group A """
        return self.contents[0]

    @property
    def b(self) -> int:
        """ group B """
        return self.contents[1]

    @property
    def c(self) -> int:
        """ group C """
        return self.contents[2]

    @property
    def d(self) -> int:
        """ group D """
        return self.contents[3]

    @property
    def e(self) -> int:
        """ group E """
        return self.contents[4]

    @property
    def f(self) -> int:
        """ group F """
        return self.contents[5]


class OctetStringDateTime(cdt.DateTime):
    """ type Time in OctetString(SIZE(12)) """
    TAG = b'\x09'
    NAME = F"{cdt.tn.OCTET_STRING}[12]"

    def __init__(self, value: bytes | bytearray | str | int | datetime.datetime | datetime.date | datetime.time = b'\x09\x0c\x07\xe4\x01\x01\xff\xff\xff\xff\xff\x80\x00\xff'):
        match value:  # TODO: common for all OctetDateTimes
            case bytes() if value[1] == len(self): super().__init__(self.TAG+value[2:])
            case bytes():                          raise ValueError(F'In {self.NAME} got tag, size: {value[0]} {value[1]}, expected {self.TAG.hex(" ")} {len(self)}')
            case _:                                super().__init__(value)

    @property
    def encoding(self) -> bytes:
        return b'\x09\x0c' + self.contents


class OctetStringDate(cdt.Date):
    """ type Time in OctetString(SIZE(5)) """
    TAG = b'\x09'
    NAME = F'{cdt.tn.OCTET_STRING}[5]'

    def __init__(self, value: bytes | bytearray | str | int | datetime.datetime | datetime.date = b'\x09\x05\x07\xe4\x01\x01\xff'):
        match value:  # TODO: replace priority case
            case bytes() if value[1] == len(self): super().__init__(self.TAG+value[2:])
            case bytes():                          raise ValueError(F'In {self.NAME} got tag, size: {value[0]} {value[1]}, expected {self.TAG.hex(" ")} {len(self)}')
            case _:                                super().__init__(value)

    @property
    def encoding(self) -> bytes:
        return b'\x09\x05' + self.contents


class OctetStringTime(cdt.Time):
    """ type Time in OctetString(SIZE(4)) """
    TAG = b'\x09'
    NAME = F'{cdt.tn.OCTET_STRING}[4]'

    def __init__(self, value: bytes | bytearray | str | int | datetime.datetime | datetime.time = b'\x09\x04\x00\x00\x00\x00'):
        match value:  # TODO: replace priority case
            case bytes() if value[1] == len(self): super().__init__(self.TAG+value[2:])
            case bytes():                          raise ValueError(F'In {self.NAME} got tag, size: {value[0]} {value[1]}, expected {self.TAG.hex(" ")} {len(self)}')
            case _:                                super().__init__(value)

    @property
    def encoding(self) -> bytes:
        return b'\x09\x04' + self.contents


class Integer0(cdt.Integer):
    """ Limited Integer only 0 """
    NAME = F'{cdt.tn.INTEGER}(0)'

    def validate(self):
        if self.decode() != 0:
            raise ValueError(F'The integer(0) must only 0,  got {self.decode()}')


if __name__ == '__main__':
    c = cdt.OctetString(bytearray((1,2,3,4,5,6)))
    a = LogicalName(c)
    a = LogicalName('1.2.3.4')
    int_hash = hash(1)
    a_hash = hash(a)
    print(a == 1)
    b = {a: 1, 1: 2}
    print(b[a])
    v = bytes.fromhex('090C07DE0C0A030A060BFF007800')
    a = DateTime(v)
    print(a.day)
    from widgets.entry import Entry
    import tkinter as tk

    class Test:
        def __init__(self, value):
            self.value = value

        def get(self, id_):
            return self.value

        def set(self, id_, value):
            self.value = value

    print(a.encoding.hex(' '))
    print(str(a))

    root = tk.Tk()
    test = Test(a)
    widget1 = Entry(master=root, id_=1, cb_set_to_source=test.set, cb_get_from_source=test.get)
    widget1.widget.grid()
    root.mainloop()
