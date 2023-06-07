from abc import ABC
from itertools import chain
from typing import TypeAlias, Self
from ..types import cdt, ut, cst
from ..types.implementations import structs


class CommonDataTypeChoiceBase(ut.CHOICE, ABC):
    """ For some attributes of some COSEM interface objects, the data type may be chosen at COSEM object instantiation, in the implementation phase
    of the COSEM server. The Server always shall send back the data type and the value of each attribute, so that together with the logical name, an
    unambiguous interpretation is ensured. The list of possible data types is defined in the “Attribute description” section of a COSEM interface
    class specification. DLMS UA 1000-1 Ed. 13. The tag of a type defined using the CHOICE keyword takes the value of the tag of the type from which
    the chosen data value is taken. ITU-T Rec. X.680 | ISO/IEC 8824-1 """
    TYPE = cdt.CommonDataType

    def __init_subclass__(cls, **kwargs):
        cls.ELEMENTS = dict()
        for t in kwargs["types"]:
            if isinstance(t, dict):  # extended choice
                cls.ELEMENTS[int.from_bytes(tuple(t.values())[0].TAG, "big")] = {k: ut.SequenceElement(v.NAME, v) for k, v in t.items()}
            elif issubclass(t, cdt.CommonDataType):
                cls.ELEMENTS[int.from_bytes(t.TAG, "big")] = ut.SequenceElement(t.NAME, t)
            else:
                raise TypeError(F"got {t.__class__} expected cdt or dict")


class SimpleDataTypeChoice(CommonDataTypeChoiceBase, types=cdt.SimpleDataType.__subclasses__()):
    """All Simple Data Types"""


class ComplexDataTypeChoice(CommonDataTypeChoiceBase, types=cdt.ComplexDataType.__subclasses__()):
    """All Complex Data Types"""


class AccessSelectorsChoice(CommonDataTypeChoiceBase, types=(cdt.NullData, cdt.Array)):
    """All Complex Data Types"""


class CommonDataTypeChoice(CommonDataTypeChoiceBase, types=chain(cdt.SimpleDataType.__subclasses__(), cdt.ComplexDataType.__subclasses__())):
    """Types of Data.value"""


class ExtendedRegisterChoice(CommonDataTypeChoiceBase,
                             types=(cdt.NullData, cdt.BitString, cdt.DoubleLongUnsigned, cdt.OctetString, cdt.VisibleString, cdt.Utf8String, cdt.Unsigned, cdt.LongUnsigned,
                                    cdt.Long64Unsigned)):
    """Types of ExtendedRegister.value"""


class RegisterChoice(CommonDataTypeChoiceBase,
                     types=(cdt.NullData, cdt.BitString, cdt.DoubleLongUnsigned, cdt.OctetString, cdt.VisibleString, cdt.Utf8String, cdt.Unsigned, cdt.LongUnsigned,
                            cdt.Long64Unsigned, cdt.DoubleLong, cdt.Integer, cdt.Long, cdt.Long64, cdt.Enum, cdt.Float32, cdt.Float64)):
    """Types of ExtendedRegister.value"""


class AnyDateTimeChoice(CommonDataTypeChoiceBase, types=(cdt.DateTime, cdt.Date, cdt.Time, {12: cst.OctetStringDateTime, 5: cst.OctetStringDate, 4: cst.OctetStringTime})):
    """Date of the event may contain the date only, the time only or both, encoded as specified in 4.1.6.1."""


simple_dt = SimpleDataTypeChoice()
complex_dt = ComplexDataTypeChoice()
common_dt = CommonDataTypeChoice()
extended_register = ExtendedRegisterChoice()
register = RegisterChoice()
access_selectors: cdt.NullData | cdt.Array = AccessSelectorsChoice()
any_date_time = AnyDateTimeChoice()


ExtendedRegisterValues: TypeAlias = cdt.NullData | cdt.BitString | cdt.DoubleLongUnsigned | cdt.OctetString | cdt.VisibleString | cdt.Utf8String | cdt.Unsigned \
                                    | cdt.LongUnsigned | cdt.Long64Unsigned
RegisterValues: TypeAlias = ExtendedRegisterValues | cdt.DoubleLong | cdt.Integer | cdt.Long | cdt.Long64 | cdt.Enum | cdt.Float32 | cdt.Float64


class RestrictionValue(ut.CHOICE):
    TYPE = (cdt.Structure, cdt.NullData)
    ELEMENTS = {0: ut.SequenceElement("no restriction apply", cdt.NullData),
                1: ut.SequenceElement("restriction by date", structs.RestrictionByDate),
                2: ut.SequenceElement("restriction by entry", structs.RestrictionByEntry)}


restriction_value = RestrictionValue()


class IdentifiedKeyInfoOptions(cdt.Enum, elements=(0, 1)):
    """"""


class KEKId(cdt.Enum, elements=(0,)):
    """"""


class WrappedKeyInfoOptions(cdt.Structure):
    kek_id: KEKId
    key_ciphered_data: cdt.OctetString


class AgreedKeyInfoOptions(cdt.Structure):
    kek_id: cdt.OctetString
    key_ciphered_data: cdt.OctetString


class KeyInfoOptions(ut.CHOICE):
    TYPE = (cdt.Enum, cdt.Structure)
    ELEMENTS = {0: ut.SequenceElement("identified_key", IdentifiedKeyInfoOptions),
                1: ut.SequenceElement("wrapped_key", WrappedKeyInfoOptions),
                2: ut.SequenceElement("agreed_key", AgreedKeyInfoOptions)}


key_info_options = KeyInfoOptions()


class StructureMixin:
    """use for cdt.Structure[Enum, CommonDataType]"""
    ELEMENTS: tuple[cdt.StructElement, cdt.StructElement]
    values: list[cdt.Enum, cdt.CommonDataType]
    __len__: int

    def __init__(self, value: bytes | tuple | list | None | bytearray | Self = None):
        def raise_error(set_value):
            raise RuntimeError(F"not can't be set {set_value} to {self}, available only set complex struct value")
        super(StructureMixin, self).__init__(value)
        self.values[0].register_cb_preset(raise_error)

    def from_sequence(self, sequence: tuple):
        if len(sequence) != len(self):
            raise ValueError(F'Struct {self.__class__.__name__} got length:{len(sequence)}, expected length:{len(self)}')
        self.values.append(self.ELEMENTS[0].TYPE(sequence[0]))
        self.values.append(self.ELEMENTS[1].TYPE(int(self.values[0])))
        self.values[1].set(sequence[1])

    def from_content(self, value: bytes):
        el_value, pdu = cdt.get_instance_and_pdu(self.ELEMENTS[0].TYPE, value)
        self.values.append(el_value)
        el_value, pdu = cdt.get_instance_and_pdu(self.ELEMENTS[1].TYPE.ELEMENTS[int(self.values[0])].TYPE, pdu)
        self.values.append(el_value)


