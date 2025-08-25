from src.DLMS_SPODES.cosem_interface_classes import collection, overview
from src.DLMS_SPODES.types import cdt, ut, cst


col = collection.Collection(
    id_=collection.ID(
        man=b'KPZ',
        f_id=collection.ParameterValue(
            par=b'',
            value=cdt.OctetString("4d324d5f33").encoding),
        f_ver=collection.ParameterValue(
            par=b'',
            value=cdt.OctetString(bytearray(b'1.3.0')).encoding)
    )
)
col.spec_map = col.get_spec()
print(col)
ass = col.add(
    class_id=overview.ClassID.ASSOCIATION_LN,
    version=overview.VERSION_1,
    logical_name=cst.LogicalName.from_obis("0.0.40.0.1.255"))