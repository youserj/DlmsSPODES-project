from abc import ABC
from itertools import chain
from typing import TypeAlias
from ..types import cdt, ut, cst


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
access_selectors = AccessSelectorsChoice()
any_date_time = AnyDateTimeChoice()


ExtendedRegisterValues: TypeAlias = cdt.NullData | cdt.BitString | cdt.DoubleLongUnsigned | cdt.OctetString | cdt.VisibleString | cdt.Utf8String | cdt.Unsigned \
                                    | cdt.LongUnsigned | cdt.Long64Unsigned
RegisterValues: TypeAlias = ExtendedRegisterValues | cdt.DoubleLong | cdt.Integer | cdt.Long | cdt.Long64 | cdt.Enum | cdt.Float32 | cdt.Float64
