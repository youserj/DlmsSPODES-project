from ...types import common_data_types as cdt


class DoubleLongUnsignedSecond(cdt.DoubleLongUnsigned):
    """for second implementation"""


class IPAddress(cdt.DoubleLongUnsigned):
    """with string parser"""

    def from_str(self, value: str) -> bytes:
        """ create ip: integer from string type ddd.ddd.ddd.ddd, ex.: 127.0.0.1 """
        raw_value = bytes()
        for separator in '... ':
            try:
                element, value = value.split(separator, 1)
            except ValueError:
                element, value = value, ''
            raw_value += self.__get_attr_element(element)
        return raw_value

    @staticmethod
    def __get_attr_element(value: str) -> bytes:
        if isinstance(value, str):
            if value == '':
                return b'\x00'
            try:
                return int(value).to_bytes(1, 'big')
            except OverflowError:
                raise ValueError(F'Int too big to convert {value}')
        else:
            raise TypeError(F'Unsupported type validation from string, got {value.__class__}')

    def __str__(self):
        return F'{self.contents[0]}.{self.contents[1]}.{self.contents[2]}.{self.contents[3]}'
