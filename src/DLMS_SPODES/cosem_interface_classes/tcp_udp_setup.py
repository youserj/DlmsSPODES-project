from ..types import cdt, cst
from ..types.type_alias import Attr
from .cosem_interface_class import ICAuto, ICAElement
from .Overview import class_id


class TCPUDPSetup(ICAuto):
    """4.9.1 TCP-UDP setup"""
    CLASS_ID = class_id.TCP_UDP_SETUP
    VERSION = 0
    A_ELEMENTS = (ICAElement(2, "TCP_UDP_port", cdt.LongUnsigned, default=4059),
                  ICAElement(3, "IP_reference", cst.LogicalName),
                  ICAElement(4, "MMS", cdt.LongUnsigned, 40, 535, 535),  # TODO: max, def not according by BlueBook
                  ICAElement(5, "nb_of_sim_conn", cdt.Unsigned, 1),
                  ICAElement(6, "inactivity_time_out", cdt.LongUnsigned, default=180))
    TCP_UDP_port: Attr
    IP_reference: Attr
    MMS: Attr
    nb_of_sim_conn: Attr
    inactivity_time_out: Attr
