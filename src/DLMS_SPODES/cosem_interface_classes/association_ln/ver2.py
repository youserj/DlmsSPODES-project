from types import common_data_types as cdt
import ver1


class AssociationLN(ver1.AssociationLN):
    """ COSEM logical devices able to establish application associations within a COSEM context using logical name referencing, model the associations
    through instances of the “Association LN” class. A COSEM logical device has one instance of this IC for each association
    the device is able to support"""
    VERSION = cdt.Unsigned(2)

    def characteristics_init(self):
        super(AssociationLN, self).characteristics_init()
        # TODO: more 2 attribute
        # TODO: more 2 methods


if __name__ == '__main__':
    a = AssociationLN('0.0.40.0.0.255')
    print(a.object_list)
    b = bytes.fromhex('01 01 02 04 12 00 08 11 00 09 06 00 00 01 00 00 FF 02 02 01 09 02 03 0F 01 16 01 00 02 03 0F 02 16 03 00 02 03 0F 03 16 03 00 02 03 0F 04 16 03 00 02 03 0F 05 16 03 00 02 03 0F 06 16 03 00 02 03 0F 07 16 03 00 02 03 0F 08 16 03 00 02 03 0F 09 16 03 00 01 06 02 02 0F 01 16 01 02 02 0F 02 16 01 02 02 0F 03 16 01 02 02 0F 04 16 01 02 02 0F 05 16 01 02 02 0F 06 16 01')
    a = ver1.ObjectListType(b)
    print(a)
    a.append()
    print(a)
