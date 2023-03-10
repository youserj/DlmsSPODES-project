from ...types import common_data_types as cdt
from ...cosem_interface_classes import cosem_interface_class as ic, overview


class ClassId(cdt.LongUnsigned):
    """ Class ID type """

    def validate(self):
        if not int(self) in overview.ClassID.get_all_id():
            raise ValueError(F'Unknown DLMS class with ID {int(self)}')
