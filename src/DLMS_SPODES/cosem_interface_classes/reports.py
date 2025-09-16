from typing import Any, Iterable
from StructResult import result
from . import cosem_interface_class as ic
from ..types import cdt
from .parameter import Parameter
from ..cosem_interface_classes import collection
from ..config_parser import get_values
from ..settings import settings


def from_obj(
        col: collection.Collection,
        obj: ic.COSEMInterfaceClasses,
        attr_index_par: tuple[int, ...]
) -> result.SimpleOrError[str]:
    if not hasattr(from_obj, "struct_pattern"):
        from_obj.struct_pattern = dict(settings.report.struct)
    ret: str = F"[{collection.get_name(obj.logical_name)}]\n"
    for i in attr_index_par:
        par = Parameter(obj.logical_name.contents).set_i(i)
        if isinstance(res_data := col.par2data(par), result.Error):
            return res_data
        a_data = res_data.value
        if isinstance(a_data, cdt.SimpleDataType):
            rep = col.par2rep(par, a_data)
            ret += F"  {obj.get_attr_element(i)}: {rep.msg}{f" {rep.unit}" if rep.unit else ""}\n"
        elif isinstance(a_data, cdt.ComplexDataType):
            ret += F"  [{obj.get_attr_element(i)}]\n"
            stack: list[tuple[Any, Any]] = [("", iter(a_data))]
            while stack:
                name, value_it = stack[-1]
                indent = F"{' ' * (len(stack) + 1)}"
                data = next(value_it, None)
                if data:
                    if not isinstance(name, str):
                        name = str(next(name))
                    if isinstance(data, cdt.Array):
                        ret += F"{indent}[{name}]\n"
                        stack.append(("*", iter(data)))
                    elif isinstance(data, cdt.Structure):
                        if (pattern := from_obj.struct_pattern.get(data.__class__.__name__)):
                            val = list(pattern)
                            val.reverse()
                            result_ = str()
                            while val:
                                match val.pop():
                                    case "%":
                                        par_ = val.pop()
                                        index = int(val.pop() + val.pop())
                                        match par_:
                                            case "n":
                                                result_ += str(data.ELEMENTS[index])
                                            case "v":
                                                result_ += str(data[index])
                                            case err:
                                                raise ValueError(F"unknown macros &{err}{index}")
                                    case symbol:
                                        result_ += symbol
                            ret += F"{indent}{result_}\n"
                        else:
                            if name=="":
                                ret += "\n"
                            else:
                                ret += F"{indent}[{name}]\n"
                            stack.append((iter(data.ELEMENTS), iter(data)))
                    else:
                        ret += F"{indent}{name}: {data}\n"
                else:
                    stack.pop()
    return result.Simple(ret)
