from .__class_init__ import *


class TCPUDPSetup(ic.COSEMInterfaceClasses):
    """ This IC allows modelling the setup of the TCP or UDP sub-layer of the COSEM TCP or UDP  based transport layer of a TCP-UDP/IP based communication profile.
     In TCP-UDP/IP based communication profiles, all AAs between a physical device hosting one or more COSEM client application processes and a physical device hosting one or more
     COSEM server APs rely on a single TCP or UDP  connection. The TCP or UDP entity is wrapped in the COSEM TCP-UDP based transport layer. Within a physical device, each
     AP - client AP or server logical device - is bound to a Wrapper Port (WPort). The binding is done with the help of the SAP Assignment object. See 4.4.5 DLMS 1000-1 Ed. 12.0.
     On the other hand, COSEM TCP  or UDP based transport layer may be capable to support more than one TCP or UDP connections, between a physical device and several peer physical
     devices hosting COSEM APs.
     When a COSEM physical device supports various data link layers - for example Ethernet and PPP - an instance of the TCP-UDP setup object is necessary for each of them. """
    NAME = cn.TCP_UDP_SETUP
    CLASS_ID = ClassID.TCP_UDP_SETUP
    VERSION = Version.V0
    A_ELEMENTS = (ic.ICAElement(an.TCP_UDP_PORT, cdt.LongUnsigned, default=4059),
                  ic.ICAElement(an.IP_REFERENCE, cst.LogicalName),
                  ic.ICAElement(an.MMS, cdt.LongUnsigned, 40, 535, 535),  # TODO: max, def not according by BlueBook
                  ic.ICAElement(an.NB_OF_SIM_CONN, cdt.Unsigned, 1),
                  ic.ICAElement(an.INACTIVITY_TIME_OUT, cdt.LongUnsigned, default=180))

    def characteristics_init(self):
        """nothing do it"""

    @property
    def TCP_UDP_port(self) -> cdt.LongUnsigned:
        return self.get_attr(2)

    @property
    def IP_reference(self) -> cst.LogicalName:
        return self.get_attr(3)

    @property
    def MMS(self) -> cdt.LongUnsigned:
        return self.get_attr(4)

    @property
    def nb_of_sim_conn(self) -> cdt.Unsigned:
        return self.get_attr(5)

    @property
    def inactivity_time_out(self) -> cdt.LongUnsigned:
        return self.get_attr(6)
