from abc import ABC
from itertools import chain
from ..types import common_data_types as cdt, useful_types as ut


class CommonDataTypeChoiceBase(ut.CHOICE, ABC):
    """ For some attributes of some COSEM interface objects, the data type may be chosen at COSEM object instantiation, in the implementation phase
    of the COSEM server. The Server always shall send back the data type and the value of each attribute, so that together with the logical name, an
    unambiguous interpretation is ensured. The list of possible data types is defined in the “Attribute description” section of a COSEM interface
    class specification. DLMS UA 1000-1 Ed. 13. The tag of a type defined using the CHOICE keyword takes the value of the tag of the type from which
    the chosen data value is taken. ITU-T Rec. X.680 | ISO/IEC 8824-1 """
    TYPE = cdt.CommonDataType


class SimpleDataTypeChoice(CommonDataTypeChoiceBase):
    """All Simple Data Type"""
    ELEMENTS = {0: ut.SequenceElement(cdt.tn.NULL_DATA, cdt.NullData),
                3: ut.SequenceElement(cdt.tn.BOOLEAN, cdt.Boolean),
                4: ut.SequenceElement(cdt.tn.BIT_STRING, cdt.BitString),
                5: ut.SequenceElement(cdt.tn.DOUBLE_LONG, cdt.DoubleLong),
                6: ut.SequenceElement(cdt.tn.DOUBLE_LONG_UNSIGNED, cdt.DoubleLongUnsigned),
                9: ut.SequenceElement(cdt.tn.OCTET_STRING, cdt.OctetString),
                10: ut.SequenceElement(cdt.tn.VISIBLE_STRING, cdt.VisibleString),
                12: ut.SequenceElement(cdt.tn.UTF8_STRING, cdt.Utf8String),
                13: ut.SequenceElement(cdt.tn.BCD, cdt.Bcd),
                15: ut.SequenceElement(cdt.tn.INTEGER, cdt.Integer),
                16: ut.SequenceElement(cdt.tn.LONG, cdt.Long),
                17: ut.SequenceElement(cdt.tn.UNSIGNED, cdt.Unsigned),
                18: ut.SequenceElement(cdt.tn.LONG_UNSIGNED, cdt.LongUnsigned),
                20: ut.SequenceElement(cdt.tn.LONG64, cdt.Long64),
                21: ut.SequenceElement(cdt.tn.LONG64_UNSIGNED, cdt.Long64Unsigned),
                22: ut.SequenceElement(cdt.tn.ENUM, cdt.Enum),
                23: ut.SequenceElement(cdt.tn.FLOAT32, cdt.Float32),
                24: ut.SequenceElement(cdt.tn.FLOAT64, cdt.Float64),
                25: ut.SequenceElement(cdt.tn.DATE_TIME, cdt.DateTime),
                26: ut.SequenceElement(cdt.tn.DATE, cdt.Date),
                27: ut.SequenceElement(cdt.tn.TIME, cdt.Time),
                # TODO: and more 28..33
                }


class ComplexDataTypeChoice(CommonDataTypeChoiceBase):
    """All Complex Data Types"""
    ELEMENTS = {0: ut.SequenceElement(cdt.tn.NULL_DATA, cdt.NullData),
                1: ut.SequenceElement(cdt.tn.ARRAY, cdt.Array),
                2: ut.SequenceElement(cdt.tn.STRUCTURE, cdt.Structure),
                19: ut.SequenceElement(cdt.tn.COMPACT_ARRAY, cdt.CompactArray)}


class AccessSelectorsChoice(CommonDataTypeChoiceBase):
    """All Complex Data Types"""
    ELEMENTS = {0: ut.SequenceElement(cdt.tn.NULL_DATA, cdt.NullData),
                1: ut.SequenceElement(cdt.tn.ARRAY, cdt.Array)}


class CommonDataTypeChoice(CommonDataTypeChoiceBase):
    """Types of Data.value"""
    ELEMENTS = dict(chain(SimpleDataTypeChoice.ELEMENTS.items(), ComplexDataTypeChoice.ELEMENTS.items()))


class ExtendedRegisterChoice(CommonDataTypeChoiceBase):
    """Types of ExtendedRegister.value"""
    ELEMENTS = {0: ut.SequenceElement(cdt.tn.NULL_DATA, cdt.NullData),
                4: ut.SequenceElement(cdt.tn.BIT_STRING, cdt.BitString),
                6: ut.SequenceElement(cdt.tn.DOUBLE_LONG_UNSIGNED, cdt.DoubleLongUnsigned),
                9: ut.SequenceElement(cdt.tn.OCTET_STRING, cdt.OctetString),
                10: ut.SequenceElement(cdt.tn.VISIBLE_STRING, cdt.VisibleString),
                12: ut.SequenceElement(cdt.tn.UTF8_STRING, cdt.Utf8String),
                17: ut.SequenceElement(cdt.tn.UNSIGNED, cdt.Unsigned),
                18: ut.SequenceElement(cdt.tn.LONG_UNSIGNED, cdt.LongUnsigned),
                21: ut.SequenceElement(cdt.tn.LONG64_UNSIGNED, cdt.Long64Unsigned)}


class RegisterChoice(CommonDataTypeChoiceBase):
    """Types of ExtendedRegister.value"""
    ELEMENTS = dict(ExtendedRegisterChoice.ELEMENTS)
    ELEMENTS.update({5: ut.SequenceElement(cdt.tn.DOUBLE_LONG, cdt.DoubleLong),
                     15: ut.SequenceElement(cdt.tn.INTEGER, cdt.Integer),
                     16: ut.SequenceElement(cdt.tn.LONG, cdt.Long),
                     20: ut.SequenceElement(cdt.tn.LONG64, cdt.Long64),
                     22: ut.SequenceElement(cdt.tn.ENUM, cdt.Enum),
                     23: ut.SequenceElement(cdt.tn.FLOAT32, cdt.Float32),
                     24: ut.SequenceElement(cdt.tn.FLOAT64, cdt.Float64)})


simple_dt = SimpleDataTypeChoice()
complex_dt = ComplexDataTypeChoice()
common_dt = CommonDataTypeChoice()
extended_register = ExtendedRegisterChoice()
register = RegisterChoice()
access_selectors = AccessSelectorsChoice()
