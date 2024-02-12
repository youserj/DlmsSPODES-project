from typing import Any
from ...types import common_data_types as cdt, implementations as impl


class SelectionAccess(cdt.Array):
    """Use as buffer in ProfileGeneric and object_list in AssociationLN"""
    selective_access: Any | None = None
    TYPE: cdt.Structure

    # @abstractmethod
    # def is_writable(self, ln: cst.LogicalName, indexes: set[int]) -> bool:
    #     """ index - DLMS object attribute index.
    #      True: DLMS object with ln and index has writable Access"""


class MulticastIPAddress(cdt.Array):
    TYPE = impl.double_long_usingneds.IPAddress
