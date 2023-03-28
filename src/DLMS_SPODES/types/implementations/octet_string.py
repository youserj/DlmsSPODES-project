from ...types import common_data_types as cdt


class LDN(cdt.OctetString):
    """for ldn. todo: check length in initialisation"""
    def manufacturer(self) -> bytes:
        return self.contents[:3]
