from . import register
from .__class_init__ import *
from ..types import choices


class ExtendedRegister(register.Register, ic.COSEMInterfaceClasses):
    """ A “Register” object stores a process value or a status value with its associated unit. The register object knows
    the nature of the process value or of the status value. The nature of the value is described by the attribute
    “logical name” using the OBIS identification system. """
    NAME = cn.EXTENDED_REGISTER
    CLASS_ID = ClassID.EXT_REGISTER
    VERSION = Version.V0
    A_ELEMENTS = (register.Register.get_attr_element(2),
                  register.Register.get_attr_element(3),
                  ic.ICAElement(an.STATUS, choices.extended_register, classifier=ic.Classifier.DYNAMIC),
                  ic.ICAElement(an.CAPTURE_TIME, cst.OctetStringDateTime, classifier=ic.Classifier.DYNAMIC))
    M_ELEMENTS = register.Register.get_meth_element(1),

    @property
    def status(self) -> choices.ExtendedRegisterValues:
        return self.get_attr(4)

    @property
    def capture_time(self) -> cdt.DateTime:
        return self.get_attr(5)


