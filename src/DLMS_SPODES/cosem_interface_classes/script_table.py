from .__class_init__ import *
from ..types import choices


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
    

class ScriptTable(ic.COSEMInterfaceClasses):
    """ The IC script table provides the possibility to trigger a series of actions by executing scripts using the execute (data) method. For that
    purpose, script table contains a table of script entries. Each table entry (script) consists of a script_identifier and a series of
    action_specifications. An action_specification activates a method of a COSEM object or modifies attributes of a COSEM object within the logical
    device. A specific script may be activated by other COSEM objects within the same logical device or from the outside. If two scripts have to be
    executed at the same time instance, then the one with the smaller index is executed first """
    CLASS_ID = ClassID.SCRIPT_TABLE
    VERSION = Version.V0
    A_ELEMENTS = ic.ICAElement("scripts", Scripts),
    M_ELEMENTS = ic.ICMElement("execute", cdt.LongUnsigned),

    def characteristics_init(self):
        self.set_attr(2, None)
        self._cbs_attr_post_init.update({2: self.__set_script_identifier_cbs})

    @property
    def scripts(self) -> Scripts:
        return self.get_attr(2)

    @property
    def execute(self) -> cdt.LongUnsigned:
        return self.get_meth(1)

    def __set_script_identifier_cbs(self):
        pass
        # try:
        #     indexes: Callable = self.entries.get_indexes
        #     self.enable_disable.firstIndexA.set_callback(indexes)
        #     self.enable_disable.firstIndexB.set_callback(indexes)
        #     self.enable_disable.lastIndexA.set_callback(indexes)
        #     self.enable_disable.lastIndexB.set_callback(indexes)
        #     self.insert.index.set_callback(indexes)
        #     self.delete.firstIndex.set_callback(indexes)
        #     self.delete.lastIndex.set_callback(indexes)
        #     print('set delete')
        # except KeyError:  # At init time
        #     print('set delete NO:')


if __name__ == '__main__':
    a = b'\x01\x04\x02\x02\x12\x00\x01\x01\x01\x02\x05\x16\x01\x12\x00F\t\x06\x00\x00`\x03\n\xff\x0f\x04\x16\x00\x02\x02\x12\x00\x02\x01\x01\x02\x05\x16\x02\x12\x00F\t\x06\x00\x00`\x03\n\xff\x0f\x01\x03\x00\x02\x02\x12\x00\x03\x01\x01\x02\x05\x16\x01\x12\x00F\t\x06\x00\x00`\x03\n\xff\x0f\x04\x16\x01\x02\x02\x12\x00\x04\x01\x01\x02\x05\x16\x02\x12\x00F\t\x06\x00\x00`\x03\n\xff\x0f\x01\x03\x01'
    b = Scripts(a)
    a = ScriptTable('0.0.10.0.0.255')
    pass
    print(a)
