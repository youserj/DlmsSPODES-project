from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable
from ...types import cdt, cst, ut
from ... import pdu_enums as pdu
from ...types.type_alias import Obis


class AccessMode(cdt.Enum, ABC):
    """ TODO: """
    @abstractmethod
    def is_writable(self) -> bool:
        ...

    @abstractmethod
    def is_readable(self) -> bool:
        ...


class AttributeAccessItem(cdt.Structure, ABC):
    """ Implemented attribute and it access . Use in Association LN """
    attribute_id: cdt.Integer
    access_mode: AccessMode
    access_selectors: cdt.NullData  # override in version

    @abstractmethod
    def abstract_marker(self):
        """dummy abstract marker"""


class AttributeAccessDescriptor(cdt.Array, ABC):
    """ Array of attribute_access_item """
    TYPE = AttributeAccessItem
    """override this"""

    @abstractmethod
    def set_read_access(self, attribute_id: cdt.Integer):
        """by attribute_id"""


@runtime_checkable
class ObjectListType(cdt._Array, Protocol):
    """ Array of object_list_element. The range for the client_SAP is 0…0x7F. The range for the server_SAP is 0x000…0x3FFF."""

    def is_writable(self, obis: Obis, indexes: set[int]) -> bool:
        """ index - DLMS object attribute index.
         True: AccessRight is WriteOnly or ReadAndWrite """

    def get_attr_access(self, obis: Obis, index: int) -> pdu.AttributeAccess: ...

    def get_meth_access(self, obis: Obis, index: int) -> pdu.MethodAccess: ...
