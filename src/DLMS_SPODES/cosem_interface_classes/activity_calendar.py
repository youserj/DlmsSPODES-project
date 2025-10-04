from typing_extensions import deprecated
from typing import Self
from .overview import VERSION_0
from .__class_init__ import *
from ..types.implementations import integers, octet_string


class Season(cdt.Structure):
    """ Defined by their starting date and a specific week_profile to be executed """
    season_profile_name: cdt.OctetString
    season_start: cst.OctetStringDateTime
    week_name: cdt.OctetString


class SeasonProfile(cdt.Array):
    """ Contains a list of seasons defined by their starting date and a specific week_profile to be executed. The list is sorted according to season_start.  """
    TYPE = Season
    values: list[Season]

    def new_element(self) -> Season:
        names: list[bytes] = [bytes(el.season_profile_name) for el in self.values]
        for new_name in (i.to_bytes(1, 'big') for i in range(256)):
            if new_name not in names:
                return Season((bytearray(new_name), None, bytearray(b'week_name?')))
        raise ValueError(F'in {self} all season names is busy')

    def sort(self, date_time: cdt.DateTime) -> Self:
        """sort by date-time
        :return now Season + next Seasons"""
        s: Season
        d_t = date_time.to_datetime()
        l = list()
        """left datetime"""
        r = list()
        """right datetime"""
        for i, s in enumerate(self):
            if (el := s.season_start.get_left_nearest_datetime(d_t)) is not None:
                l.append((i, el))
            if (el := s.season_start.get_right_nearest_datetime(d_t)) is not None:
                r.append((i, el))
        l.sort(key=lambda it: it[1])
        r.sort(key=lambda it: it[1])
        now = l[-1][0]
        indexes: list[int] = [now]
        for el in r:
            if el[0] == now:
                continue
            else:
                indexes.append(el[0])
        sorted_data = self.__class__()
        for i in indexes:
            sorted_data.append(self[i])
        return sorted_data


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

    def new_element(self) -> WeekProfile:
        """return default WeekProfile with vacant week_profile_name, existed day ID and insert callback for validate change DayID"""
        names: list[bytes] = [bytes(el.week_profile_name) for el in self.values]
        for new_name in (i.to_bytes(1, 'big') for i in range(256)):
            if new_name not in names:
                return WeekProfile((bytearray(new_name), *[0]*7))
        raise ValueError(F'in {self} all week names is busy')

    def get_week_profile_names(self) -> tuple[cdt.OctetString, ...]:
        return tuple((el.week_profile_name for el in self.values))


class DayProfileAction(cdt.Structure):
    """ Scheduled action is defined by a script to be executed and the corresponding activation time (start_time). """
    start_time: cst.OctetStringTime
    script_logical_name: cst.LogicalName
    script_selector: cdt.LongUnsigned

    def __lt__(self, other: Self):
        return self.start_time.to_time() < other.start_time.to_time()


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

    def get_day_ids(self) -> tuple[cdt.Unsigned, ...]:
        return tuple((day_profile.day_id for day_profile in self.values))

    def normalize(self) -> bool:
        d_p: DayProfile
        res = False
        for d_p in self:
            if (new := DaySchedule(sorted(d_p.day_schedule))) != d_p.day_schedule:
                res = True
                d_p.day_schedule.__dict__["values"] = new.values
        return res


class ActivityCalendar(ic.COSEMInterfaceClasses):
    """DLMS UA 1000-1 Ed. 14 4.5.5 Activity calendar"""
    CLASS_ID = ClassID.ACTIVITY_CALENDAR
    VERSION = VERSION_0
    A_ELEMENTS = (ic.ICAElement("calendar_name_active", octet_string.ID),
                  ic.ICAElement("season_profile_active", SeasonProfile),
                  ic.ICAElement("week_profile_table_active", WeekProfileTable),
                  ic.ICAElement("day_profile_table_active", DayProfileTable),
                  ic.ICAElement("calendar_name_passive", octet_string.ID),
                  ic.ICAElement("season_profile_passive", SeasonProfile),
                  ic.ICAElement("week_profile_table_passive", WeekProfileTable),
                  ic.ICAElement("day_profile_table_passive", DayProfileTable),
                  ic.ICAElement("activate_passive_calendar_time", cst.OctetStringDateTime))
    M_ELEMENTS = ic.ICMElement(
        NAME="activate_passive_calendar",
        DATA_TYPE=integers.Only0),

    @property
    def calendar_name_active(self) -> octet_string.ID:
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
    def calendar_name_passive(self) -> octet_string.ID:
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

    @classmethod
    def ActivatePassiveCalendar(cls, value=None) -> integers.Only0:
        return cls.M_ELEMENTS[0].DATA_TYPE

    def validate(self):
        def validate_seasons(index: int):
            def handle_duplicates(name: str):
                nonlocal index, duplicates
                if len(duplicates) != 0:
                    raise ic.ObjectValidationError(
                        ln=self.logical_name,
                        i=index,
                        message=F"find duplicate {name}: {', '.join(map(str, duplicates))} in {self.getAElement(index).unwrap()}")
                index -= 1

            days: list[DayProfile.day_id] = []
            duplicates: set[DayProfile.day_id] | set[WeekProfile.week_profile_name] | set[Season.season_profile_name] = set()
            for it in self.get_attr(index):
                if it.day_id not in days:
                    days.append(it.day_id)
                else:
                    duplicates.add(it.day_id)
            handle_duplicates("day_id")
            weeks: list[WeekProfile.week_profile_name] = []
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
                            message=F"in {self.getAElement(index).unwrap()} got {week_profile} with day_id: {week_profile[i]}; expected: {', '.join(map(str, days))}")
            handle_duplicates("week_profile_name")
            seasons: list[Season.season_profile_name] = []
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
