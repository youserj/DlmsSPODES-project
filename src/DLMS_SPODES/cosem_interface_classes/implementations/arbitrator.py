from ..arbitrator import Arbitrator
from ... import settings


match settings.get_current_language():
    case settings.Language.ENGLISH:        from ...Values.EN import actors
    case settings.Language.RUSSIAN:        from ...Values.RU import actors


class SPODES3Arbitrator(Arbitrator):
    """Cosem3 7.3.18"""
    actors = (actors.MANUAL,
              actors.LOCAL_1,
              actors.LOCAL_2,
              actors.LOCAL_3,
              actors.LOCAL_4,
              actors.LOCAL_5,
              actors.LOCAL_6,
              actors.LOCAL_7)
