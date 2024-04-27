import unittest
from itertools import permutations
from struct import pack
from src.DLMS_SPODES.types import cdt, cst, ut, cosemClassID as classID
from src.DLMS_SPODES.cosem_interface_classes import collection


class TestType(unittest.TestCase):

    def test_ProfileGeneric(self):
        cont = list()
        coll = collection.Collection()
        ln = cst.LogicalName("0.0.96.1.1.255")
        # for i in range(100_000):
        #     cont.append(collection.Data(cst.LogicalName("0.0.96.1.1.255")))
        class_id = classID.DATA
        version = cdt.Unsigned(0)
        buf = bytearray(6)
        for i, j in permutations(range(100), 2):
            # coll.add(class_id=class_id, version=version, logical_name=cst.LogicalName(F"0.{i}.96.1.1.{j}"))
            # coll.add(class_id=class_id, version=version, logical_name=cst.LogicalName(bytearray((0, i, 96, 1, 1, j))))
            coll.add(class_id=class_id, version=version, logical_name=cst.LogicalName(pack(">8B", 9, 6, 0, i, 96, 1, 1, j)))
        print(len(coll))
