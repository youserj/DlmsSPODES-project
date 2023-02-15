from .__class_init__ import *


class IECLocalPortSetup(ic.COSEMInterfaceClasses):
    """ This IC allows modelling the configuration of communication ports using the protocols specified in IEC 62056-21:2002. Several ports can be configured. """
    NAME = cn.IEC_LOCAL_PORT_SETUP
    CLASS_ID = ut.CosemClassId(class_id.IEC_LOCAL_PORT_SETUP)
    VERSION = cdt.Unsigned(1)

    def characteristics_init(self):
        """# TODO: not released ... """
