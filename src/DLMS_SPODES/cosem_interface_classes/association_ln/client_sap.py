from ...types import cdt


class ClientSAP(cdt.Enum, elements=(0, 1, 0x10, 0x20, 0x30, 0x40, 0x50, 0x60)):  # TODO: REWRITE elements here
    """ IEC 62056-46 2002 6.4.2.3 Reserved special HDLC addresses p.40. IS15952ver2 """
    TAG = b'\x0f'


class ClientSAPConst(cdt.Constant, ClientSAP): ...

NO_STATION = ClientSAPConst(0)
MANAGEMENT_PROCESS = ClientSAPConst(1)
PUBLIC = ClientSAPConst(0x10)
READER = ClientSAPConst(0x20)
CONFIGURATOR = ClientSAPConst(0x30)
