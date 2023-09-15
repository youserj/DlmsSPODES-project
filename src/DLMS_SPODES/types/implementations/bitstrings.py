from ...types import common_data_types as cdt
from ...config_parser import get_values

base = get_values("DLMS", "Conformance")


# TODO: join with cdt.FlagMixin
class Conformance(cdt.BitString):
    ELEMENTS = ("reserved-zero",
                "general-protection",
                "general-block-transfer",
                "read",
                "write",
                "unconfirmed-write",
                "reserved-six",
                "reserved-seven",
                "attribute0-supported-with-set",
                "priority-mgmt-supported",
                "attribute0-supported-with-get",
                "block-transfer-with-get-or-read",
                "block-transfer-with-set-or-write",
                "block-transfer-with-action",
                "multiple-references",
                "information-report",
                "data-notification",
                "access",
                "parameterized-access",
                "get",
                "set",
                "selective-access",
                "event-notification",
                "action")
    if base is not None:
        ELEMENTS = tuple(base[el] for el in ELEMENTS)
    default = '011111111111111111111111'  # zero only 1 bit

    def __init__(self, value: bytes | bytearray | str | int | cdt.BitString = None):
        super(Conformance, self).__init__(value)
        if self.ELEMENTS is not None and len(self) != len(self.ELEMENTS):
            raise ValueError(F'For {self.__class__.__name__} get {len(self)} bits, expected {len(self.ELEMENTS)}')

    def __len__(self):
        return len(self.ELEMENTS)

    def from_bytes(self, value: bytes) -> bytes:
        length, pdu = cdt.get_length_and_pdu(value[1:])
        if length != len(self):
            raise ValueError(F'Got {length=}, expected {len(self)}')
        match value[:1]:
            case self.TAG if len(self) <= len(pdu) * 8: return pdu[:3]
            case self.TAG:                              raise ValueError(F'Got pdu length:{len(pdu)}, expected at least {len(self) >> 3}')
            case _ as error:                            raise TypeError(F'Expected {self.NAME} type, got {cdt.get_common_data_type_from(error).NAME}')

    def from_str(self, value: str) -> bytes:
        value = value + '0' * ((8 - len(self)) % 8)
        list_ = [value[count:(count + 8)] for count in range(0, len(self), 8)]
        value = b''
        for byte in list_:
            value += int(byte, base=2).to_bytes(1, byteorder='little')
        return value

    def from_int(self, value: int) -> bytes:
        if value < 0:
            raise ValueError
        res = 0
        start_bit = 2 ** (len(self) - 1)
        for i in range(len(self)):
            if value & (1 << i):
                res += start_bit >> i
        return res.to_bytes(len(self) // 8, byteorder='big')

    def from_bytearray(self, value: bytearray) -> bytes:
        return bytes(value)

    @classmethod
    def get_values(cls) -> list[str]:
        """ TODO: """
        return cls.ELEMENTS

    def validate_from(self, value: str, cursor_position: int) -> tuple[str, int]:
        """ return validated value and cursor position. TODO: copypast FlagMixin """
        type(self)(value=value.zfill(len(self)))
        return value, cursor_position

    @property
    def general_protection(self) -> int:
        return self.decode()[1]

    @property
    def general_block_transfer(self) -> int:
        return self.decode()[2]

    @property
    def selective_access(self) -> int:
        return self.decode()[21]
