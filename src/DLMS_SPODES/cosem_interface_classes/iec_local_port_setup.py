from .cosem_interface_class import ICAuto, Cardinality


class IECLocalPortSetup(ICAuto):
    """ This IC allows modelling the configuration of communication ports using the protocols specified in IEC 62056-21:2002. Several ports can be configured. """
    CLASS_ID = 19
    VERSION = 1
    CARDINALITY = Cardinality()
