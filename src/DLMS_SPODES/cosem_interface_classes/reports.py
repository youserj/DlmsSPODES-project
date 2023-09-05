from .collection import ic
from typing import Any


def get_obj_report(
        obj: ic.COSEMInterfaceClasses,
        attr_index_par: dict[int, Any]) -> str:
    ret = str()
    ret += F"[{obj.NAME}]\n"
    for i, par in attr_index_par.items():
        if par is None:
            ret += F"  {obj.get_attr_element(i).NAME}: {obj.get_attr(i)}\n"
    return ret
