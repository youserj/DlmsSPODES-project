import datetime
from typing import Callable, Iterator
from . import special_days_table as sdt
from .__class_init__ import *
from ..types.implementations import integers


class Season(cdt.Structure):
    """ Defined by their starting date and a specific week_profile to be executed """
    season_profile_name: cdt.OctetString
    season_start: cst.OctetStringDateTime
    week_name: cdt.OctetString


class SeasonProfile(cdt.Array):
    """ Contains a list of seasons defined by their starting date and a specific week_profile to be executed. The list is sorted according to season_start.  """
    TYPE = Season
    get_week_names: Callable
    values: list[Season]
    cb_get_week_profile_names: Callable[[], tuple[cdt.OctetString, ...]]

    def new_element(self) -> Season:
        names: list[bytes] = [bytes(el.season_profile_name) for el in self.values]
        for new_name in (i.to_bytes(1, 'big') for i in range(256)):
            if new_name not in names:
                if len(week_names := self.cb_get_week_profile_names()) == 0:
                    raise ValueError(F"{WeekProfile.__class__.__name__} container is absense")
                return Season((bytearray(new_name), None, week_names[0]))
        raise ValueError(F'in {self} all season names is busy')

    def append_validate(self, element: Season):
        """validate season_profile_name from array"""
        if cdt.OctetString(element.season_profile_name) in (val.season_profile_name for val in self.values):
            raise ValueError(F'{element.values} already exist in {self}')
        else:
            """validate OK"""


class WeekProfile(cdt.Structure):
    """ For each week_profile, the day_profile for every day of a week is identified. """
    week_profile_name: cdt.OctetString
    monday: cdt.Unsigned
    tuesday: cdt.Unsigned
    wednesday: cdt.Unsigned
    thursday: cdt.Unsigned
    friday: cdt.Unsigned
    saturday: cdt.Unsigned
    sunday: cdt.Unsigned


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
                if len(days_id := self.cb_get_day_ids()) == 0:
                    raise ValueError("days_id container is absense")
                return WeekProfile((bytearray(new_name), *[days_id[0]]*7))
        raise ValueError(F'in {self} all week names is busy')

    def append_validate(self, element: WeekProfile):
        """"""
        if (err := cdt.OctetString(element.week_profile_name)) in (val.week_profile_name for val in self.values):
            raise ValueError(F"can't append in {self}, {err} already exist")
        else:
            """validate OK"""

    def get_week_profile_names(self) -> tuple[cdt.OctetString, ...]:
        return tuple((el.week_profile_name for el in self.values))


class DayProfileAction(cdt.Structure):
    """ Scheduled action is defined by a script to be executed and the corresponding activation time (start_time). """
    start_time: cst.OctetStringTime
    script_logical_name: cst.LogicalName
    script_selector: cdt.LongUnsigned


# TODO: make unique by start_time
class DaySchedule(cdt.Array):
    """ Contains an array of day_profile_action. """
    TYPE = DayProfileAction
    values: list[DayProfileAction]


class DayProfile(cdt.Structure):
    """ list of Scheduled actions is defined by a script to be executed and the corresponding activation time (start_time) with day ID. """
    day_id: cdt.Unsigned
    day_schedule: DaySchedule


class DayProfileTable(cdt.Array):
    """ Contains an array of day_profiles, identified by their day_id. For each day_profile, a list of scheduled actions is defined by a script to be
    executed and the corresponding activation time (start_time). The list is sorted according to start_time.  """
    TYPE = DayProfile
    values: list[DayProfile]

    def new_element(self) -> DayProfile:
        """return default DayProfile with vacant Day ID"""
        day_ids: list[int] = [int(el.day_id) for el in self.values]
        for i in range(0xff):
            if i not in day_ids:
                return DayProfile((i, None))
        raise ValueError(F'in {self} all days ID is busy')

    def append_validate(self, element: DayProfile):
        """validate and insert callback for validate change DayID"""
        if (err := cdt.Unsigned(element.day_id)) in (day_profile.day_id for day_profile in self.values):
            raise ValueError(F"can't append in {self}, {err} already exist")
        else:
            """validate OK"""

    def get_day_ids(self) -> tuple[cdt.Unsigned, ...]:
        return tuple((day_profile.day_id for day_profile in self.values))


class ActivityCalendar(ic.COSEMInterfaceClasses):
    """DLMS UA 1000-1 Ed. 14 4.5.5 Activity calendar"""
    CLASS_ID = classID.ACTIVITY_CALENDAR
    VERSION = Version.V0
    A_ELEMENTS = (ic.ICAElement("calendar_name_active", cdt.OctetString),
                  ic.ICAElement("season_profile_active", SeasonProfile),
                  ic.ICAElement("week_profile_table_active", WeekProfileTable),
                  ic.ICAElement("day_profile_table_active", DayProfileTable),
                  ic.ICAElement("calendar_name_passive", cdt.OctetString),
                  ic.ICAElement("season_profile_passive", SeasonProfile),
                  ic.ICAElement("week_profile_table_passive", WeekProfileTable),
                  ic.ICAElement("day_profile_table_passive", DayProfileTable),
                  ic.ICAElement("activate_passive_calendar_time", cst.OctetStringDateTime))
    M_ELEMENTS = ic.ICMElement("activate_passive_calendar", integers.Only0),

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

    def validate(self):
        def validate_seasons(index: int):
            def handle_duplicates(name: str):
                nonlocal index, duplicates
                if len(duplicates) != 0:
                    raise ic.ObjectValidationError(
                        ln=self.logical_name,
                        i=index,
                        message=F"find duplicate {name}: {', '.join(map(str, duplicates))} in {self.get_attr_element(index)}")
                index -= 1

            days: list[DayProfile.day_id] = list()
            duplicates: set[DayProfile.day_id] | set[WeekProfile.week_profile_name] | set[Season.season_profile_name] = set()
            for it in self.get_attr(index):
                if it.day_id not in days:
                    days.append(it.day_id)
                else:
                    duplicates.add(it.day_id)
            handle_duplicates("day_id")
            weeks: list[WeekProfile.week_profile_name] = list()
            for week_profile in self.get_attr(index):
                if week_profile.week_profile_name not in weeks:
                    weeks.append(week_profile.week_profile_name)
                else:
                    duplicates.add(week_profile.week_profile_name)
                for i in range(1, 7):
                    if week_profile[i] not in days:
                        raise ic.ObjectValidationError(
                            ln=self.logical_name,
                            i=index,
                            message=F"in {self.get_attr_element(index)} got {week_profile} with day_id: {week_profile[i]}; expected: {', '.join(map(str, days))}")
            handle_duplicates("week_profile_name")
            seasons: list[Season.season_profile_name] = list()
            for season in self.get_attr(index):
                if season.season_profile_name not in seasons:
                    seasons.append(season.season_profile_name)
                else:
                    duplicates.add(season.season_profile_name)
                if season.week_name not in weeks:
                    raise ic.ObjectValidationError(
                        ln=self.logical_name,
                        i=index,
                        message=F"in {self.get_attr_element(index)} got {season} with: {season.week_name}, expected: {', '.join(map(str, weeks))}")
            handle_duplicates("season_profile_name")

        validate_seasons(5)
        validate_seasons(9)
