from .__class_init__ import *
from ..types.implementations import structs, integers
from .overview import VERSION_0


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


class Arbitrator(ic.COSEMInterfaceClasses):
    """DLMS UA 1000-1 Ed. 14 4.5.12 Arbitrator"""
    CLASS_ID = ClassID.ARBITRATOR
    VERSION = VERSION_0
    A_ELEMENTS = (ic.ICAElement("actions", Actions),
                  ic.ICAElement("permission_table", PermissionsTable),
                  ic.ICAElement("weightings_table", WeightingsTable),
                  ic.ICAElement("most_recent_requests_table", MostRecentRequestTable, classifier=ic.Classifier.DYNAMIC),
                  ic.ICAElement("last_outcome", cdt.Unsigned, min=0, default=0, classifier=ic.Classifier.DYNAMIC))  # TODO: max = n what it?
    M_ELEMENTS = (ic.ICMElement("request_action", RequestAction),
                  ic.ICMElement("reset", integers.INTEGER_0))
    actors: tuple[str] = tuple()
    """name actors container"""

    @property
    def actions(self) -> Actions:
        return self.get_attr(2)

    @property
    def permissions_table(self) -> PermissionsTable:
        return self.get_attr(3)

    @property
    def weightings_table(self) -> WeightingsTable:
        return self.get_attr(4)

    @property
    def most_recent_request_table(self) -> MostRecentRequestTable:
        return self.get_attr(5)

    @property
    def last_outcome(self) -> cdt.Unsigned:
        return self.get_attr(6)

    def __check_permission_table(self):
        """set length actor_permission be same as action array size if it not valid"""
        if len(self.permissions_table) > 0:
            for actor in self.permissions_table:
                if len(actor) != len(self.actions):
                    actor.set(ActorPermissions('0'*len(self.actions)))
                else:
                    """lenght is correct, change is not required """
        else:
            """not was loaded"""
