from ..types.implementations import structs
from ..types.implementations import integers
from typing import Optional
from ..types import cdt
from .cosem_interface_class import ICAElement, ICMElement, Classifier, ICAuto
from .Overview import class_id


class Actions(cdt.Array):
    """ Array of key_data """
    TYPE = structs.ActionItem


class ActorPermissions(cdt.BitString):
    """TODO: """


class PermissionsTable(cdt.Array):
    TYPE = ActorPermissions
    __iter__: ActorPermissions
    __get_item__: ActorPermissions


class ActorActionWeight(cdt.LongUnsigned):
    """TODO: make any thing"""


class ActorWeightingList(cdt.Array):
    TYPE = ActorActionWeight


class WeightingsTable(cdt.Array):
    TYPE = ActorWeightingList


class MostRecentRequest(cdt.BitString):
    """TODO: """


class MostRecentRequestTable(cdt.Array):
    TYPE = MostRecentRequest


class RequestAction(cdt.Structure):
    """Defines the actions that are requested by an actorDefines the actions that are requested by an actor"""
    request_actor: cdt.Unsigned
    request_action_list: cdt.BitString


class Arbitrator(ICAuto):
    """4.5.12 Arbitrator"""
    CLASS_ID = class_id.ARBITRATOR
    VERSION = 0
    A_ELEMENTS = (ICAElement(2, "actions", Actions),
                  ICAElement(3, "permission_table", PermissionsTable),
                  ICAElement(4, "weightings_table", WeightingsTable),
                  ICAElement(5, "most_recent_requests_table", MostRecentRequestTable, classifier=Classifier.DYNAMIC),
                  ICAElement(6, "last_outcome", cdt.Unsigned, min=0, default=0, classifier=Classifier.DYNAMIC))  # TODO: max = n what it?
    M_ELEMENTS = (ICMElement(1, "request_action", RequestAction),
                  ICMElement(2, "reset", integers.INTEGER_0))
    actors: tuple[str] = tuple()
    """name actors container"""
    actions: Optional[Actions]
    permissions_table: Optional[PermissionsTable]
    weightings_table: Optional[WeightingsTable]
    most_recent_request_table: Optional[MostRecentRequestTable]
    last_outcome: Optional[cdt.Unsigned]
