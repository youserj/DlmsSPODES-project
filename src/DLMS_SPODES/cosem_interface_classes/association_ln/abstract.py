from abc import ABC, abstractmethod
from ...types import cdt


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
