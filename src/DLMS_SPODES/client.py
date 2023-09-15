from functools import lru_cache
from dataclasses import dataclass
from .types import cdt, cst
from . import pdu_enums as pdu
from .cosem_interface_classes import collection
from . import exceptions as exc


@dataclass
class Settings:
    current_ass_id: int


class Client:
    objects: collection.Collection
    settings: Settings

    @lru_cache(maxsize=1000)
    def is_writable(self, ln: cst.LogicalName, index: int, association_id: int = None) -> bool:
        if not association_id:
            association_id = self.current_association.id
        match self.objects.getASSOCIATION(association_id).object_list.get_attr_access(ln, index):
            case pdu.AttributeAccess.NO_ACCESS | pdu.AttributeAccess.READ_ONLY | pdu.AttributeAccess.AUTHENTICATED_READ_ONLY:
                return False
            case pdu.AttributeAccess.WRITE_ONLY | pdu.AttributeAccess.READ_AND_WRITE:
                return True
            case pdu.AttributeAccess.AUTHENTICATED_WRITE_ONLY | pdu.AttributeAccess.AUTHENTICATED_READ_AND_WRITE:
                if self.settings.cipher.security == Security.AUTHENTICATION:
                    return True
                else:
                    return False
            case err:
                raise exc.ITEApplication(F"unsupport access: {err}")

    @lru_cache(maxsize=1000)
    def is_readable(self, ln: cst.LogicalName, index: int, association_id: int = None) -> bool:
        if not association_id:
            association_id = self.current_association.id
        match self.objects.getASSOCIATION(association_id).object_list.get_attr_access(ln, index):
            case pdu.AttributeAccess.NO_ACCESS | pdu.AttributeAccess.WRITE_ONLY | pdu.AttributeAccess.AUTHENTICATED_WRITE_ONLY:
                return False
            case pdu.AttributeAccess.READ_ONLY | pdu.AttributeAccess.READ_AND_WRITE:
                return True
            case pdu.AttributeAccess.AUTHENTICATED_READ_ONLY | pdu.AttributeAccess.AUTHENTICATED_READ_AND_WRITE:
                if self.settings.cipher.security == Security.AUTHENTICATION:
                    return True
                else:
                    return False
            case err:
                raise exc.ITEApplication(F"unsupport access: {err}")

