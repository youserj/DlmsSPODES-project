from typing import Self
from COSEMpdu.data import Structure, OctetString, Array, DateTime, Unsigned, LongUnsigned
from ..types.implementations import integers
from ..types import cst
from .cosem_interface_class import ICAElement, ICMElement, ICAuto
from ..types.type_alias import Attr


class Season(Structure):
    """season"""
    season_profile_name: OctetString
    season_start: cst.OctetStringDateTime
    week_name: OctetString


class SeasonProfile(Array[Season]):
    """attribute season_profile"""

    def sort(self, date_time: DateTime) -> Self:  # TODO: fix with new API
        """sort by date-time
        :return now Season + next Seasons"""
        s: Season
        d_t = date_time.to_datetime()
        l = []
        """left datetime"""
        r = []
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


class WeekProfile(Structure):
    """week_profile"""
    week_profile_name: OctetString
    monday: Unsigned
    tuesday: Unsigned
    wednesday: Unsigned
    thursday: Unsigned
    friday: Unsigned
    saturday: Unsigned
    sunday: Unsigned


class WeekProfileTable(Array[WeekProfile]):
    """ Contains an array of week_profiles to be used in the different seasons. For each week_profile, the day_profile for every day of a week is
    identified. """

    def new_element(self) -> WeekProfile:  # TODO: fix with new API
        """return default WeekProfile with vacant week_profile_name, existed day ID and insert callback for validate change DayID"""
        names: list[bytes] = [bytes(el.week_profile_name) for el in self.values]
        for new_name in (i.to_bytes(1, "big") for i in range(256)):
            if new_name not in names:
                return WeekProfile((bytearray(new_name), *[0]*7))
        raise ValueError(F"in {self} all week names is busy")

    def get_week_profile_names(self) -> tuple[OctetString, ...]:  # TODO: fix with new API
        return tuple((el.week_profile_name for el in self.values))


class DayProfileAction(Structure):
    """day_profile_action"""
    start_time: cst.OctetStringTime
    script_logical_name: cst.LogicalName
    script_selector: LongUnsigned

    def __lt__(self, other: Self) -> bool:
        return self.start_time.to_time() < other.start_time.to_time()


DaySchedule = Array[DayProfileAction]  # TODO: make unique by start_time
"""day_schedule"""


class DayProfile(Structure):
    """day_profile"""
    day_id: Unsigned
    day_schedule: DaySchedule


class DayProfileTable(Array[DayProfile]):
    """attribute day_profile_table"""

    def new_element(self) -> DayProfile:  # TODO: fix with new API
        """return default DayProfile with vacant Day ID"""
        day_ids: list[int] = [int(el.day_id) for el in self.values]
        for i in range(0xff):
            if i not in day_ids:
                return DayProfile((i, None))
        raise ValueError(F"in {self} all days ID is busy")

    def get_day_ids(self) -> tuple[Unsigned, ...]:  # TODO: fix with new API
        return tuple((day_profile.day_id for day_profile in self.values))

    def normalize_(self) -> bool:  # TODO: fix with new API
        d_p: DayProfile
        res = False
        for d_p in self:
            if (new := DaySchedule(sorted(d_p.day_schedule))) != d_p.day_schedule:
                res = True
                d_p.day_schedule.__dict__["values"] = new.values
        return res


class ActivityCalendar(ICAuto):
    """DLMS UA 1000-1 Ed. 14 4.5.5 Activity calendar"""
    CLASS_ID = 20
    VERSION = 0
    A_ELEMENTS = (
        ICAElement(2, "calendar_name_active", OctetString),
        ICAElement(3, "season_profile_active", SeasonProfile),
        ICAElement(4, "week_profile_table_active", WeekProfileTable),
        ICAElement(5, "day_profile_table_active", DayProfileTable),
        ICAElement(6, "calendar_name_passive", OctetString),
        ICAElement(7, "season_profile_passive", SeasonProfile),
        ICAElement(8, "week_profile_table_passive", WeekProfileTable),
        ICAElement(9, "day_profile_table_passive", DayProfileTable),
        ICAElement(10, "activate_passive_calendar_time", cst.OctetStringDateTime))
    M_ELEMENTS = ICMElement(1, "activate_passive_calendar", integers.IntegerValue0),
    calendar_name_active: Attr
    season_profile_active: Attr
    week_profile_table_active: Attr
    day_profile_table_active: Attr
    calendar_name_passive: Attr
    season_profile_passive: Attr
    week_profile_table_passive: Attr
    day_profile_table_passive: Attr
    activate_passive_calendar_time: Attr

    def validate(self):  # TODO: fix with new API
        def validate_seasons(index: int):
            def handle_duplicates(name: str):
                nonlocal index, duplicates
                if len(duplicates) != 0:
                    raise ObjectValidationError(
                        ln=self.logical_name,
                        i=index,
                        message=F"find duplicate {name}: {", ".join(map(str, duplicates))} in {self.getAElement(index).unwrap()}")
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
                        raise ObjectValidationError(
                            ln=self.logical_name,
                            i=index,
                            message=F"in {self.getAElement(index).unwrap()} got {week_profile} with day_id: {week_profile[i]}; expected: {", ".join(map(str, days))}")
            handle_duplicates("week_profile_name")
            seasons: list[Season.season_profile_name] = []
            for season in self.get_attr(index):
                if season.season_profile_name not in seasons:
                    seasons.append(season.season_profile_name)
                else:
                    duplicates.add(season.season_profile_name)
                if season.week_name not in weeks:
                    raise ObjectValidationError(
                        ln=self.logical_name,
                        i=index,
                        message=F"in {self.get_attr_element(index)} got {season} with: {season.week_name}, expected: {", ".join(map(str, weeks))}")
            handle_duplicates("season_profile_name")

        validate_seasons(5)
        validate_seasons(9)
