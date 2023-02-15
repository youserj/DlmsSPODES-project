from __future__ import annotations
from .__class_init__ import *
from types.implements import structs, integers


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
    values: tuple[cdt.Unsigned, cdt.BitString]
    ELEMENTS = (cdt.StructElement(cdt.se.REQUEST_ACTOR, cdt.Unsigned),
                cdt.StructElement(cdt.se.REQUEST_ACTION_LIST, cdt.BitString))

    @property
    def request_actor(self) -> cdt.Unsigned:
        return self.values[0]

    @property
    def request_action_list(self) -> cdt.BitString:
        return self.values[1]


class Arbitrator(ic.COSEMInterfaceClasses):
    """LMS UA 1000-1 Ed. 14 4.5.12 Arbitrator"""
    NAME = cn.ARBITRATOR
    CLASS_ID = ut.CosemClassId(class_id.ARBITRATOR)
    VERSION = cdt.Unsigned(0)
    A_ELEMENTS = (ic.ICAElement(an.ACTIONS, Actions),
                  ic.ICAElement(an.PERMISSION_TABLE, PermissionsTable),
                  ic.ICAElement(an.WEIGHTINGS_TABLE, WeightingsTable),
                  ic.ICAElement(an.MOST_RECENT_REQUESTS_TABLE, MostRecentRequestTable),
                  ic.ICAElement(an.LAST_OUTCOME, cdt.Unsigned, min=0, default=0))  # TODO: max = n what it?

    M_ELEMENTS = (ic.ICMElement(mn.REQUEST_ACTION, RequestAction),
                  ic.ICMElement(mn.RESET, integers.Only0))
    actors: tuple[str] = tuple()
    """name actors container"""

    def characteristics_init(self):
        self.set_attr(2, None)
        self.actions.register_cb_post_set(self.__check_permission_table)
        self.set_attr(3, None)
        self.set_attr(4, None)
        self.set_attr(5, None)

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

    @property
    def request_action(self) -> RequestAction:
        return self .get_meth(1)

    @property
    def reset(self) -> integers.Only0:
        return self .get_meth(2)

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

    def get_action_names(self) -> list[str]:
        """return names of methods by ordering actions"""
        return [self.collection.get_script_names(ln, selector) for ln, selector in self.actions]
