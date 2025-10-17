from ..types import choices, cdt, cst
from ..types.type_alias import Attr
from .cosem_interface_class import ICAuto, ICAElement, ICMElement
from .Overview import class_id


class ServiceId(cdt.Enum, elements=(1, 2)):
    """defines which action to be applied to the referenced object."""


class ActionSpecification(cdt.Structure):
    """ Specifies the different scripts, i.e. the lists of actions. The first attribute (logical_name) has index 1, the first specific method has
    index 1 as well. NOTE The action_specification is limited to activate methods that do not produce any response (from the server to the client). """
    service_id: ServiceId
    class_id: cdt.LongUnsigned
    logical_name: cst.LogicalName
    index: cdt.Integer
    parameter: choices.common_dt


class Actions(cdt.Array):
    """ Specifies the list of action specification """
    TYPE = ActionSpecification


class Script(cdt.Structure):
    """ Specifies the different scripts. The script_identifier 0 is reserved. If specified with an execute method, it results in a null script (no actions to perform)"""
    script_identifier: cdt.LongUnsigned
    actions: Actions


class Scripts(cdt.Array):
    """ Specifies the lists of actions """
    TYPE = Script
    __get_item__: Script

    def new_element(self) -> Script:
        """return default Script with vacant script_identifier"""
        # todo: make common function by ID element
        el: Script
        day_ids: list[int] = [int(el.script_identifier) for el in self.values]
        for i in range(0xffff):
            if i not in day_ids:
                return Script((i, None))
        raise ValueError(F"in {self} all <script_identifier> is busy")


class ScriptTable(ICAuto):
    """Script table"""
    CLASS_ID = class_id.SCRIPT_TABLE
    VERSION = 0
    A_ELEMENTS = ICAElement(2, "scripts", Scripts),
    M_ELEMENTS = ICMElement(1, "execute", cdt.LongUnsigned),
    scripts: Attr
