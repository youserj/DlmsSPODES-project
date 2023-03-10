from ..cosem_interface_classes import cosem_interface_class as ic, attr_indexes as ai
from ..cosem_interface_classes.overview import ClassID, Version
from ..types import common_data_types as cdt, cosem_service_types as cst, useful_types as ut
from ..settings import get_current_language, Language

match get_current_language():
    case Language.ENGLISH: from ..Values.EN import class_names as cn, attr_names as an, meth as mn, enum_names as en
    case Language.RUSSIAN: from ..Values.RU import class_names as cn, attr_names as an, meth as mn, enum_names as en
