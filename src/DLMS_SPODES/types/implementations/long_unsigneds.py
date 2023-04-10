from ...types import common_data_types as cdt
from DLMS_SPODES import cosem_interface_classes


class ClassId(cdt.LongUnsigned):
    """ Class ID type """

    def validate(self):
        if not int(self) in cosem_interface_classes.overview.ClassID.get_all_id():
            raise ValueError(F'Unknown DLMS class with ID {int(self)}')
