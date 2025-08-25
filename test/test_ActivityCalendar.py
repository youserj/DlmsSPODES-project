import unittest
from src.DLMS_SPODES.types import cdt, cst, ut
from src.DLMS_SPODES.cosem_interface_classes import collection
from src.DLMS_SPODES.cosem_interface_classes import activity_calendar
from src.DLMS_SPODES.cosem_interface_classes.overview import ClassID, VERSION_0
from src.DLMS_SPODES import exceptions as exc


class TestType(unittest.TestCase):

    def test_Limiter(self):
        col = collection.get_collection(
            manufacturer=b"KPZ",
            server_type=collection.ParameterValue(
                par=bytes.fromhex("0000600102ff02"),
                value=cdt.OctetString("4d324d5f33").encoding),
            server_ver=collection.ParameterValue(
                par=bytes.fromhex("0000000201ff02"),
                value=cdt.OctetString(bytearray(b"1.4.15")).encoding))


        col.set_manufacturer(b'KPZ')
        col.set_firm_ver(collection.ParameterValue(
                par=bytes.fromhex("0000000201ff02"),
                value=cdt.OctetString(bytearray(b"1.4.0")).encoding))
        col.spec_map = col.get_spec()
        tem = col.add(class_id=ClassID.REGISTER,
                version=VERSION_0,
                logical_name=cst.LogicalName.from_obis("0.0.96.9.0.255"))
        tem.set_attr(2, bytes.fromhex('10 00 1b'))
        lim = col.add(class_id=ClassID.LIMITER,
                version=VERSION_0,
                logical_name=cst.LogicalName.from_obis("0.0.17.0.5.255"))
        # lim.set_attr(3, bytes.fromhex('11 00 00 00 00'))
        self.assertRaises(exc.EmptyObj, lim.set_attr, 3, bytes.fromhex('11 00 00 00 00'))
        lim.set_attr(2, bytes.fromhex('02 03 12 00 03 09 06 00 00 60 09 00 ff 0f 02'))
        print(col, lim)

    def test_ActivityCalendar(self):
        obj: collection.ActivityCalendar = collection.ActivityCalendar("00 00 0d 00 00 ff")
        obj.day_profile_table_active.set(bytes.fromhex("01 01 02 02 11 00 01 01 02 03 09 04 00 00 ff ff 09 06 00 00 0a 00 64 ff 12 00 01"))
        obj.day_profile_table_active.append((1, [("00:00", "00 00 00 00 00 00", 1)]))
        obj.week_profile_table_active.set(bytes.fromhex("01 01 02 08 09 07 44 65 66 61 75 6c 74 11 01 11 00 11 00 11 00 11 00 11 00 11 00"))
        obj.week_profile_table_active.append()
        # obj.week_profile_table_active.append((bytearray(b'\x00'), 0, 0, 0, 0, 0, 0, 0))
        obj.season_profile_active.set(bytes.fromhex("01 01 02 03 09 07 44 65 66 61 75 6c 74 09 0c ff ff 01 01 ff ff ff ff ff 80 00 00 09 07 44 65 66 61 75 6c 73"))
        obj.season_profile_active.append()
        obj.validate()

    def test_d(self):
        d_p = activity_calendar.DaySchedule([
            ("00:00", "00 00 10 00 64 ff", 1),
            ("02:00", "00 00 10 00 64 ff", 2),
            ("01:00", "00 00 10 00 64 ff", 3),
        ])
        sort = sorted(d_p)
        new = activity_calendar.DaySchedule(sort)
        print(d_p, sort)