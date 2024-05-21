from typing import Any, TypeAlias
from dataclasses import dataclass
from .collection import ic, cdt
from ..cosem_interface_classes import collection
from ..config_parser import get_values
import logging


Level: TypeAlias = logging.INFO | logging.WARN | logging.ERROR


@dataclass(frozen=True)
class Report:
    mess: str
    lev: Level = logging.INFO

    def __str__(self):
        return self.mess


def get_obj_report(
        obj: ic.COSEMInterfaceClasses,
        attr_index_par: tuple[int | Any, ...]) -> str:
    struct_report: dict | None = get_values("DLMS", "report", "struct")
    ret = str()
    ret += F"[{collection.get_name(obj.logical_name)}]\n"
    for i in attr_index_par:
        if isinstance(i, int):
            pass
        else:
            i, par = i[0], i[1:]
        value = obj.get_attr(i)
        if isinstance(value, cdt.SimpleDataType):
            match obj, i:
                case collection.impl.data.DLMSDeviceIDObject(), 2: value = value.to_str()
                case _: pass
            if isinstance(value, cdt.OctetString):
                pass
            if hasattr(value, "report"):
                value = value.report
            ret += F"  {obj.get_attr_element(i)}: {value}\n"
        elif isinstance(value, cdt.ComplexDataType):
            ret += F"  [{obj.get_attr_element(i)}]\n"
            stack: list = [("", iter(value))]
            while stack:
                name, value_it = stack[-1]
                indent = F"{' '*(len(stack) + 1)}"
                value = next(value_it, None)
                if value:
                    if not isinstance(name, str):
                        name = next(name).NAME
                    if isinstance(value, cdt.Array):
                        ret += F"{indent}[{name}]\n"
                        stack.append(("*", iter(value)))
                    elif isinstance(value, cdt.Structure):
                        if struct_report and (pattern := struct_report.get(value.__class__.__name__)):
                            val = list(pattern)
                            val.reverse()
                            result = str()
                            while val:
                                i = val.pop()
                                match i:
                                    case "%":
                                        par = val.pop()
                                        index = int(val.pop() + val.pop())
                                        match par:
                                            case "n":
                                                result += value.ELEMENTS[index].NAME
                                            case "v":
                                                result += str(value[index])
                                            case err:
                                                raise ValueError(F"unknown macros &{err}{index}")
                                    case symbol:
                                        result += symbol
                            ret += F"{indent}{result}\n"
                        else:
                            if name == "":
                                ret += "\n"
                            else:
                                ret += F"{indent}[{name}]\n"
                            stack.append((iter(value.ELEMENTS), iter(value)))
                    else:
                        ret += F"{indent}{name}: {value}\n"
                else:
                    stack.pop()
    return ret
