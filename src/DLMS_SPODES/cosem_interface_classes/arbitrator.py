from ..types.implementations import structs
from ..types.implementations import integers
from COSEMpdu.data import Array, Structure, BitString, LongUnsigned, Unsigned
from .cosem_interface_class import ICAElement, ICMElement, Classifier, ICAuto
from ..types.type_alias import Attr


Actions = Array[structs.ActionItem]
"""actions"""


class ActorPermissions(BitString):
    """actor_permissions"""


PermissionsTable = Array[ActorPermissions]
"""permissions_table"""


class ActorActionWeight(LongUnsigned):
    """actor_action_weight"""


ActorWeightingList = Array[ActorActionWeight]
"""actor_weighting_list"""
WeightingsTable = Array[ActorWeightingList]
"""weightings_table"""


class MostRecentRequest(BitString):
    """most_recent_request"""


MostRecentRequestTable = Array[MostRecentRequest]
"""most_recent_request_table"""


class RequestAction(Structure):
    """Defines the actions that are requested by an actorDefines the actions that are requested by an actor"""
    request_actor: Unsigned
    request_action_list: BitString


class Arbitrator(ICAuto):
    """4.5.12 Arbitrator"""
    CLASS_ID = 68
    VERSION = 0
    A_ELEMENTS = (
        ICAElement(2, "actions", Actions),
        ICAElement(3, "permission_table", PermissionsTable),
        ICAElement(4, "weightings_table", WeightingsTable),
        ICAElement(5, "most_recent_requests_table", MostRecentRequestTable, classifier=Classifier.DYNAMIC),
        ICAElement(6, "last_outcome", Unsigned, min=0, default=0, classifier=Classifier.DYNAMIC))  # TODO: max = n what it?
    M_ELEMENTS = (
        ICMElement(1, "request_action", RequestAction),
        ICMElement(2, "reset", integers.IntegerValue0))
    actors: tuple[str] = tuple()  # TODO: make new class or instance argument
    """name actors container"""
    actions: Attr
    permissions_table: Attr
    weightings_table: Attr
    most_recent_request_table: Attr
    last_outcome: Attr
