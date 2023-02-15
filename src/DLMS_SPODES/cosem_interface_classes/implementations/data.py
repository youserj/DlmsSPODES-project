from ..data import Data, ic, an, cdt, cst


class Unsigned(Data):
    """ with value type: Unsigned """
    A_ELEMENTS = ic.ICAElement(an.VALUE, cdt.Unsigned, classifier=ic.Classifier.DYNAMIC),


class OctetStringDateTime(Data):
    """ with value type: Unsigned """
    A_ELEMENTS = ic.ICAElement(an.VALUE, cst.OctetStringDateTime, classifier=ic.Classifier.DYNAMIC),


class OpeningBody(Data):
    """ RU. 0.0.96.51.0.255. СТО_34.01-5.1-006-2019v3. E 12.1 """
    A_ELEMENTS = ic.ICAElement(an.VALUE, cdt.Unsigned, classifier=ic.Classifier.DYNAMIC),


class SealUnsigned(cdt.Unsigned):
    @property
    def report(self) -> str:
        def get_name(value: int):
            """ СПОДЭСv.3 Е.12.5"""
            match value & 0b11:
                case 0: return "Не определено"
                case 1: return "Обжата"
                case 2: return "Взломана"
                case 3: return "Последущие вскрытия"
        return F"Электронные пломбы: корпуса - {get_name(int(self) & 0b11)}, крышки клеммников - {get_name((int(self) >> 2) & 0b11)}"


class SealStatus(Data):
    """ RU. 0.0.96.51.5.255. СТО_34.01-5.1-006-2019v3. E 12.1 """
    A_ELEMENTS = ic.ICAElement(an.VALUE, SealUnsigned, classifier=ic.Classifier.DYNAMIC),


class TerminalsCoverOpeningState(Data):
    """ RU. 0.0.96.51.1.255. СТО_34.01-5.1-006-2019v3. E 12.2 """
    A_ELEMENTS = ic.ICAElement(an.VALUE, cdt.Unsigned, classifier=ic.Classifier.DYNAMIC),


class BitMapData(cdt.Structure):
    values: tuple[cst.OctetStringDateTime, cst.OctetStringDateTime, cdt.OctetString]
    ELEMENTS = (cdt.StructElement(cdt.se.START_TIME, cst.OctetStringDateTime),
                cdt.StructElement(cdt.se.STOP_TIME, cst.OctetStringDateTime),
                cdt.StructElement(cdt.se.ITE_BIT_MAP, cdt.OctetString))

    @property
    def start_time(self) -> cst.OctetStringDateTime:
        """time of start show bitmap"""
        return self.values[0]

    @property
    def stop_time(self) -> cst.OctetStringDateTime:
        """time of stop show bitmap"""
        return self.values[1]

    @property
    def bitmap_data(self) -> cdt.OctetString:
        """data with bitmap format"""
        return self.values[2]


class ITEBitMap(Data):
    """ITE 0.0.128.160.0.255. Use for send struct lcd screen bitmap(BMP) with start/stop period to server"""
    A_ELEMENTS = ic.ICAElement(an.VALUE, BitMapData, classifier=ic.Classifier.STATIC),
