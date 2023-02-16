from ...types import common_data_types as cdt
from ...cosem_interface_classes import cosem_interface_class as ic


class ClassId(cdt.LongUnsigned):
    """ Class ID type """

    def validate(self):
        if ic.is_class_id_exist(int(self)):
            raise ValueError(F'Unknown DLMS class with ID {int(self)}')
