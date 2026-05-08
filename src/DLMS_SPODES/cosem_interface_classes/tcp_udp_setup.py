from COSEMpdu.data import Unsigned, LongUnsigned
from ..types import cst
from ..types.type_alias import Attr
from .cosem_interface_class import ICAuto, ICAElement


class TCPUDPSetup(ICAuto):
    """4.9.1 TCP-UDP setup"""
    CLASS_ID = 41
    VERSION = 0
    A_ELEMENTS = (
        ICAElement(2, "TCP_UDP_port", LongUnsigned, default=4059),
        ICAElement(3, "IP_reference", cst.LogicalName),
        ICAElement(4, "MMS", LongUnsigned, 40, 535, 535),  # max, def not according by BlueBook
        ICAElement(5, "nb_of_sim_conn", Unsigned, 1),
        ICAElement(6, "inactivity_time_out", LongUnsigned, default=180))
    TCP_UDP_port: Attr
    IP_reference: Attr
    MMS: Attr
    nb_of_sim_conn: Attr
    inactivity_time_out: Attr
