from COSEMpdu.data import OctetString


class LDN(OctetString):
    """for ldn. todo: check length in initialisation"""
    def get_manufacturer(self) -> bytes:
        return self.contents[:3]


class ID(OctetString):
    """for all implementation of Identifiers"""
