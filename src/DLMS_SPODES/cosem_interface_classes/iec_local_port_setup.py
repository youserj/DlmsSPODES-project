from .__class_init__ import *


class IECLocalPortSetup(ic.COSEMInterfaceClasses):
    """ This IC allows modelling the configuration of communication ports using the protocols specified in IEC 62056-21:2002. Several ports can be configured. """
    CLASS_ID = ClassID.IEC_LOCAL_PORT_SETUP
    VERSION = Version.V1

    def characteristics_init(self):
        """# TODO: not released ... """
