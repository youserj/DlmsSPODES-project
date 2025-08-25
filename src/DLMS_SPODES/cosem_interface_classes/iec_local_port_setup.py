from ..cosem_interface_classes import cosem_interface_class as ic
from .overview import ClassID, VERSION_1


class IECLocalPortSetup(ic.COSEMInterfaceClasses):
    """ This IC allows modelling the configuration of communication ports using the protocols specified in IEC 62056-21:2002. Several ports can be configured. """
    CLASS_ID = ClassID.IEC_LOCAL_PORT_SETUP
    VERSION = VERSION_1

    def characteristics_init(self) -> None:
        """# TODO: not released ... """
