from __future__ import annotations
import datetime
from typing import Callable, Iterator
from . import special_days_table as sdt
from .__class_init__ import *
from ..types.implementations import integers


class Season(cdt.Structure):
    """ Defined by their starting date and a specific week_profile to be executed """
    values: tuple[cdt.OctetString, cst.OctetStringDateTime, cdt.OctetString]
    ELEMENTS = (cdt.StructElement(cdt.se.SEASON_PROFILE_NAME, cdt.OctetString),
                cdt.StructElement(cdt.se.SEASON_START, cst.OctetStringDateTime),
                cdt.StructElement(cdt.se.WEEK_NAME, cdt.OctetString))

    @property
    def season_profile_name(self) -> cdt.OctetString:
        """season_profile_name is a user defined name identifying the current season_profile"""
        return self.values[0]

    @property
    def season_start(self) -> cst.OctetStringDateTime:
        """season_start defines the starting time of the season, formatted as set in for date_time.
        REMARK The current season is terminated by the season_start of the next season """
        return self.values[1]

    @property
    def week_name(self) -> cdt.OctetString:
        """week_name defines the week_profile active in this season"""
        return self.values[2]


class SeasonProfile(cdt.Array):
    """ Contains a list of seasons defined by their starting date and a specific week_profile to be executed. The list is sorted according to season_start.  """
    get_week_names: Callable
    TYPE = Season
    values: list[Season]
    cb_get_week_profile_names: Callable[[], tuple[cdt.OctetString, ...]]

    def new_element(self) -> Season:
        names: list[bytes] = [el.season_profile_name.decode() for el in self.values]
        for new_name in (i.to_bytes(1, 'big') for i in range(256)):
            if new_name not in names:
                return Season((bytearray(new_name), None, self.cb_get_week_profile_names()[0]))
        raise ValueError(F'in {self} all season names is busy')

    def append_validate(self, element: Season):
        self.__check_season_profile_name(element.season_profile_name)
        self.__check_week_profile_name(element.week_name)
        element.season_profile_name.register_cb_preset(self.__check_season_profile_name)
        element.week_name.register_cb_preset(self.__check_week_profile_name)

    def __check_season_profile_name(self, value):
        """validate season_profile_name from array"""
        if cdt.OctetString(value) in (val.season_profile_name for val in self.values):
            raise ValueError(F'{cdt.OctetString(value)} already exist in {self}')
        else:
            """validate OK"""

    def __check_week_profile_name(self, value=None):
        """validate week_name from array"""
        if cdt.OctetString(value) not in self.cb_get_week_profile_names():
            raise ValueError(F'{cdt.OctetString(value)} is absence in week_profile_name')
        else:
            """validate OK"""


class WeekProfile(cdt.Structure):
    """ For each week_profile, the day_profile for every day of a week is identified. """
    values: tuple[cdt.OctetString, cdt.Unsigned, cdt.Unsigned, cdt.Unsigned, cdt.Unsigned, cdt.Unsigned, cdt.Unsigned, cdt.Unsigned]
    ELEMENTS = (cdt.StructElement(cdt.se.WEEK_PROFILE_NAME, cdt.OctetString),
                cdt.StructElement(cdt.se.MONDAY, cdt.Unsigned),
                cdt.StructElement(cdt.se.TUESDAY, cdt.Unsigned),
                cdt.StructElement(cdt.se.WEDNESDAY, cdt.Unsigned),
                cdt.StructElement(cdt.se.THURSDAY, cdt.Unsigned),
                cdt.StructElement(cdt.se.FRIDAY, cdt.Unsigned),
                cdt.StructElement(cdt.se.SATURDAY, cdt.Unsigned),
                cdt.StructElement(cdt.se.SUNDAY, cdt.Unsigned))

    @property
    def week_profile_name(self) -> cdt.OctetString:
        """User defined name identifying the current week_profile"""
        return self.values[0]

    # TODO: make monday-sunday as enumerator from day_id of day_profile_table
    @property
    def monday(self) -> cdt.Unsigned:
        """Monday defines the day_profile valid on Monday"""
        return self.values[1]

    @property
    def tuesday(self) -> cdt.Unsigned:
        return self.values[2]

    @property
    def wednesday(self) -> cdt.Unsigned:
        return self.values[3]

    @property
    def thursday(self) -> cdt.Unsigned:
        return self.values[4]

    @property
    def friday(self) -> cdt.Unsigned:
        return self.values[5]

    @property
    def saturday(self) -> cdt.Unsigned:
        return self.values[6]

    @property
    def sunday(self) -> cdt.Unsigned:
        return self.values[7]

    def get_days_id(self) -> tuple[int, ...]:
        """ return days IDs container as integers """
        return self.monday.decode(), self.tuesday.decode(), self.wednesday.decode(), self.thursday.decode(), self.friday.decode(), self.saturday.decode(), self.sunday.decode()


class WeekProfileTable(cdt.Array):
    """ Contains an array of week_profiles to be used in the different seasons. For each week_profile, the day_profile for every day of a week is
    identified. """
    TYPE = WeekProfile
    values: list[WeekProfile]
    cb_get_day_ids: Callable[[], tuple[cdt.Unsigned]]

    def new_element(self) -> WeekProfile:
        """return default WeekProfile with vacant week_profile_name, existed day ID and insert callback for validate change DayID"""
        names: list[bytes] = [el.week_profile_name.decode() for el in self.values]
        for new_name in (i.to_bytes(1, 'big') for i in range(256)):
            if new_name not in names:
                return WeekProfile((bytearray(new_name), *[self.cb_get_day_ids()[0]]*7))
        raise ValueError(F'in {self} all week names is busy')

    def append_validate(self, element: WeekProfile):
        self.__check_week_profile_name(element.week_profile_name)
        self.__check_day_id(element.monday)
        self.__check_day_id(element.tuesday)
        self.__check_day_id(element.wednesday)
        self.__check_day_id(element.thursday)
        self.__check_day_id(element.friday)
        self.__check_day_id(element.saturday)
        self.__check_day_id(element.sunday)
        element.week_profile_name.register_cb_preset(self.__check_week_profile_name)
        element.monday.register_cb_preset(self.__check_day_id)
        element.tuesday.register_cb_preset(self.__check_day_id)
        element.wednesday.register_cb_preset(self.__check_day_id)
        element.thursday.register_cb_preset(self.__check_day_id)
        element.friday.register_cb_preset(self.__check_day_id)
        element.saturday.register_cb_preset(self.__check_day_id)
        element.sunday.register_cb_preset(self.__check_day_id)

    def __check_day_id(self, value):
        """validate day_id from DayProfile"""
        if cdt.Unsigned(value) not in self.cb_get_day_ids():
            raise ValueError(F'{cdt.Unsigned(value)} is absent in day_profile_table')
        else:
            """validate OK"""

    def __check_week_profile_name(self, value=None):
        """validate week_name from array"""
        if cdt.OctetString(value) in (val.week_profile_name for val in self.values):
            raise ValueError(F'{cdt.OctetString(value)} already exist in {self}')
        else:
            """validate OK"""

    def get_week_profile_names(self) -> tuple[cdt.OctetString, ...]:
        return tuple((el.week_profile_name for el in self.values))


class DayProfileAction(cdt.Structure):
    """ Scheduled action is defined by a script to be executed and the corresponding activation time (start_time). """
    values: tuple[cst.OctetStringTime, cst.LogicalName, cdt.LongUnsigned]
    ELEMENTS = (cdt.StructElement(cdt.se.START_TIME, cst.OctetStringTime),
                cdt.StructElement(cdt.se.SCRIPT_LOGICAL_NAME, cst.LogicalName),
                cdt.StructElement(cdt.se.SCRIPT_SELECTOR, cdt.LongUnsigned))

    @property
    def start_time(self) -> cst.OctetStringTime:
        """defines the time when the script is to be executed (no wildcards); the format follows the rules set in for time"""
        return self.values[0]

    @property
    def script_logical_name(self) -> cst.LogicalName:
        """defines the logical name of the “Script table” object"""
        return self.values[1]

    @property
    def script_selector(self) -> cdt.LongUnsigned:
        """ defines the script_identifier of the script to be executed. TODO: make getter from object with script_logical_name """
        return self.values[2]


# TODO: make unique by start_time
class DaySchedule(cdt.Array):
    """ Contains an array of day_profile_action. """
    TYPE = DayProfileAction
    values: list[DayProfileAction]


class DayProfile(cdt.Structure):
    """ list of Scheduled actions is defined by a script to be executed and the corresponding activation time (start_time) with day ID. """
    #   user defined identifier, identifying the current day_profile
    values: tuple[cdt.Unsigned, DaySchedule]
    ELEMENTS: tuple[cdt.StructElement, cdt.StructElement] = (cdt.StructElement(cdt.se.DAY_ID, cdt.Unsigned),
                                                             cdt.StructElement(cdt.se.DAY_SCHEDULE, DaySchedule))

    @property
    def day_id(self) -> cdt.Unsigned:
        return self.values[0]

    @property
    def day_schedule(self) -> DaySchedule:
        return self.values[1]


class DayProfileTable(cdt.Array):
    """ Contains an array of day_profiles, identified by their day_id. For each day_profile, a list of scheduled actions is defined by a script to be
    executed and the corresponding activation time (start_time). The list is sorted according to start_time.  """
    TYPE = DayProfile
    values: list[DayProfile]

    def new_element(self) -> DayProfile:
        """return default DayProfile with vacant Day ID"""
        day_ids: list[int] = [el.day_id.decode() for el in self.values]
        for i in range(0xff):
            if i not in day_ids:
                return DayProfile((i, None))
        raise ValueError(F'in {self} all days ID is busy')

    def append_validate(self, element: DayProfile):
        """validate and insert callback for validate change DayID"""
        self.__check_day_id(element.day_id)
        element.day_id.register_cb_preset(self.__check_day_id)

    def get_day_ids(self) -> tuple[cdt.Unsigned, ...]:
        return tuple((day_profile.day_id for day_profile in self.values))

    def __check_day_id(self, value):
        """validate day_id from DayProfile"""
        if cdt.Unsigned(value) in (day_profile.day_id for day_profile in self.values):
            raise ValueError(F'{cdt.Unsigned(value)} already exist in {self}')
        else:
            """validate OK"""


class ActivityCalendar(ic.COSEMInterfaceClasses):
    """ An instance of the “Activity calendar” class is typically used to handle different tariff structures. It is a definition of scheduled actions
    inside the meter, which follow the classical way of calendar based schedules by defining seasons, weeks… It can coexist with the more general
    object “Schedule” and can even overlap with it. If actions are scheduled for the same activation time in an object “Schedule” and in the
    object “Activity calendar”, the actions triggered by the “Schedule” object are executed first.
    After a power failure, only the “last action” missed from the object “Activity calendar” is executed (delayed). This is to ensure proper
    tariffication after power up. If a “Schedule” object is present, then the missed “last action” of the “Activity calendar” must be executed at the
    correct time within the sequence of actions requested by the “Schedule” object.
    The “Activity calendar” defines the activation of certain scripts, which can perform different activities inside the logical device. The interface
    to the object “Script table” is the same as for the object “Schedule”. If an instance of the interface class “Special days table” is available,
    relevant entries there take precedence over the “Activity calendar” object driven selection of a day profile. The day profile referenced in the
    “Special days table” activates the day_schedule of the day_profile_table in the “Activity calendar” object by referencing through the day_id. """
    NAME = cn.ACTIVITY_CALENDAR
    CLASS_ID = ut.CosemClassId(class_id.ACTIVITY_CALENDAR)
    VERSION = cdt.Unsigned(0)
    A_ELEMENTS = (ic.ICAElement(an.CALENDAR_NAME_ACTIVE, cdt.OctetString),
                  ic.ICAElement(an.SEASON_PROFILE_ACTIVE, SeasonProfile),
                  ic.ICAElement(an.WEEK_PROFILE_TABLE_ACTIVE, WeekProfileTable),
                  ic.ICAElement(an.DAY_PROFILE_TABLE_ACTIVE, DayProfileTable),
                  ic.ICAElement(an.CALENDAR_NAME_PASSIVE, cdt.OctetString),
                  ic.ICAElement(an.SEASON_PROFILE_PASSIVE, SeasonProfile),
                  ic.ICAElement(an.WEEK_PROFILE_TABLE_PASSIVE, WeekProfileTable),
                  ic.ICAElement(an.DAY_PROFILE_TABLE_PASSIVE, DayProfileTable),
                  ic.ICAElement(an.ACTIVATE_PASSIVE_CALENDAR_TIME, cst.OctetStringDateTime))
    M_ELEMENTS = ic.ICMElement(mn.ACTIVATE_PASSIVE_CALENDAR, integers.Only0),

    def characteristics_init(self):
        # Attributes called …_active are currently active, attributes called …_passive will be activated by the specific
        # method activate_passive_calendar.
        self.set_attr(ai.DAY_PROFILE_TABLE_ACTIVE, None)
        self.set_attr(ai.WEEK_PROFILE_TABLE_ACTIVE, None)
        self.set_attr(ai.SEASON_PROFILE_ACTIVE, None)
        self.set_attr(ai.DAY_PROFILE_TABLE_PASSIVE, None)
        self.set_attr(ai.WEEK_PROFILE_TABLE_PASSIVE, None)
        self.set_attr(ai.SEASON_PROFILE_PASSIVE, None)

        self.week_profile_table_active.cb_get_day_ids = self.day_profile_table_active.get_day_ids
        self.week_profile_table_passive.cb_get_day_ids = self.day_profile_table_passive.get_day_ids
        self.season_profile_active.cb_get_week_profile_names = self.week_profile_table_active.get_week_profile_names
        self.season_profile_passive.cb_get_week_profile_names = self.week_profile_table_passive.get_week_profile_names

    @property
    def calendar_name_active(self) -> cdt.OctetString:
        return self.get_attr(2)

    @property
    def season_profile_active(self) -> SeasonProfile:
        return self.get_attr(3)

    @property
    def week_profile_table_active(self) -> WeekProfileTable:
        return self.get_attr(4)

    @property
    def day_profile_table_active(self) -> DayProfileTable:
        return self.get_attr(5)

    @property
    def calendar_name_passive(self) -> cdt.OctetString:
        return self.get_attr(6)

    @property
    def season_profile_passive(self) -> SeasonProfile:
        return self.get_attr(7)

    @property
    def week_profile_table_passive(self) -> WeekProfileTable:
        return self.get_attr(8)

    @property
    def day_profile_table_passive(self) -> DayProfileTable:
        return self.get_attr(9)

    @property
    def activate_passive_calendar_time(self) -> cst.OctetStringDateTime:
        return self.get_attr(10)

    @property
    def activate_passive_calendar(self) -> integers.Only0:
        return self.get_meth(1)

    def __register_cb_check_day_id(self, attr_index: int):
        try:
            match attr_index:
                case ai.WEEK_PROFILE_TABLE_ACTIVE: self.week_profile_table_active.cb_check_day_id = self.day_profile_table_active.check_day_id
                case ai.WEEK_PROFILE_TABLE_PASSIVE: self.week_profile_table_passive.cb_check_day_id = self.day_profile_table_passive.check_day_id
        except AttributeError:
            raise AttributeError(F'для attr: {attr_index} не хватает таблицы активных суточных профилей')
        except KeyError:
            raise AttributeError(F'для attr: {attr_index} не хватает таблицы активных суточных профилей')

    def __register_cb_check_week_profile_name(self, attr_index: int):
        try:
            match attr_index:
                case ai.SEASON_PROFILE_ACTIVE: self.season_profile_active.cb_check_week_profile_name = self.week_profile_table_active.check_week_profile_name
                case ai.SEASON_PROFILE_PASSIVE: self.season_profile_passive.cb_check_week_profile_name = self.week_profile_table_passive.check_week_profile_name
        except AttributeError:
            raise AttributeError(F'для attr: {attr_index} не хватает таблицы активных недельных профилей')
        except KeyError:
            raise AttributeError(F'для attr: {attr_index} не хватает таблицы активных недельных профилей')

    def get_current_season(self, server_time: datetime.datetime = None) -> Season:
        """ current server season by current time """
        server_time = self.collection.current_time if server_time is None else server_time
        active_season: tuple[Season | None, datetime.datetime] = None, datetime.datetime(datetime.MINYEAR, 1, 1, tzinfo=datetime.timezone.utc)
        if self.season_profile_active is None:
            raise AttributeError(F'{self}: attribute Season profile is empty. Need receive it from server')
        for season in self.season_profile_active:
            season: Season
            left_point = season.season_start.get_left_nearest_datetime(server_time)
            if active_season[1] < left_point:
                active_season = season, left_point
        if active_season[0] is None:
            raise AttributeError('Season Not found in Activity calendar object')
        else:
            return active_season[0]

    def get_current_week(self, server_time: datetime.datetime = None) -> WeekProfile:
        """ current server week by current time """
        season = self.get_current_season(server_time)
        if self.week_profile_table_active is None:
            raise AttributeError(F'{self}: attribute Week profile is empty. Need receive it from server')
        for week_profile in self.week_profile_table_active:
            week_profile: WeekProfile
            if week_profile.week_profile_name == season.week_name:
                return week_profile
        raise AttributeError('Week Not found in Activity calendar object')

    def get_current_day(self, server_time: datetime.datetime = None) -> DayProfile:
        """ current server day by current time """
        server_time = self.collection.current_time if server_time is None else server_time
        special_day_table: sdt.SpecialDaysTable = self.collection.special_day_table
        day_id = special_day_table.get_day_id_of_current_special_day(server_time)
        if day_id is None:
            weekday = server_time.weekday()+1
            week = self.get_current_week(server_time)
            day_id = week[weekday]
        for day_profile in self.day_profile_table_active:
            day_profile: DayProfile
            if day_profile.day_id == day_id:
                return day_profile
        raise AttributeError(F'Day Id: {day_id} not found in Day profile table active')

    def get_current_action(self) -> DayProfileAction:
        """ current server day action by current time """
        server_time = self.collection.current_time
        day = self.get_current_day(server_time)
        active: tuple[DayProfileAction | None, datetime.time] = None, datetime.time(hour=0, minute=0, second=0)
        for day_profile_action in day.day_schedule:
            day_profile_action: DayProfileAction
            left_point = day_profile_action.start_time.get_left_nearest_time(server_time.time())
            if left_point is not None and active[1] < left_point:
                active = day_profile_action, left_point
        if active[0] is None:
            raise AttributeError('Action Not found in Activity calendar object')
        else:
            return active[0]

    def get_current_rate(self) -> int:
        """ return script selector as rate number or AttributeError """
        return self.get_current_action().script_selector.decode()

    def get_index_with_attributes(self, in_init_order: bool = False) -> Iterator[tuple[int, cdt.CommonDataType | None]]:
        """ override common method """
        if in_init_order:
            return iter(((1, self.get_attr(1)),
                        (2, self.get_attr(2)),
                        (5, self.get_attr(5)),
                        (4, self.get_attr(4)),
                        (3, self.get_attr(3)),
                        (6, self.get_attr(6)),
                        (9, self.get_attr(9)),
                        (8, self.get_attr(8)),
                        (7, self.get_attr(7)),
                        (10, self.get_attr(10))))
        else:
            return super(ActivityCalendar, self).get_index_with_attributes()

