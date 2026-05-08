from typing import Final
from COSEMpdu.data import BitString, DoubleLong, DoubleLongUnsigned, OctetString, Array, Integer, Long, Unsigned, LongUnsigned, Enum, Structure
from ...types import cst
from ..cosem_interface_class import ICAuto, ICAElement, ICMElement, Classifier
from ...types.type_alias import Attr
from ...types.implementations import integers


class ChargeType(Enum):
    """attribute charge_type"""
    CONSUMPTION_BASED_COLLECTION: Final = 0
    TIME_BASED_COLLECTION: Final = 1
    PAYMENT_EVENT_BASED_COLLECTION: Final = 2


class ChargePerUnitScalingType(Structure):
    """charge_per_unit_scaling_type"""
    commodity_scale: Integer
    price_scale: Integer


class CommodityReferenceType(Structure):
    """commodity_reference_type"""
    class_id: LongUnsigned
    logical_name: OctetString
    attribute_index: Integer


class ChargeTableElement(Structure):
    """charge_table_element"""
    index: OctetString
    charge_per_unit: Long


class UnitChargeActive(Structure):
    """unit_charge_active"""
    charge_per_unit_scaling: ChargePerUnitScalingType
    commodity_reference: CommodityReferenceType
    charge_table: Array[ChargeTableElement]


class Charge(ICAuto):
    """4.6.4 Charge"""
    CLASS_ID = 113
    VERSION = 0
    A_ELEMENTS = (
        ICAElement(2, "total_amount_paid", DoubleLong, classifier=Classifier.DYNAMIC),
        ICAElement(3, "charge_type", ChargeType, classifier=Classifier.STATIC),
        ICAElement(4, "priority", Unsigned, classifier=Classifier.STATIC),
        ICAElement(5, "unit_charge_active", UnitChargeActive, classifier=Classifier.STATIC),
        ICAElement(6, "unit_charge_passive", UnitChargeActive, classifier=Classifier.STATIC),
        ICAElement(7, "unit_charge_activation_time", cst.OctetStringDateTime, classifier=Classifier.STATIC),
        ICAElement(8, "period", DoubleLongUnsigned, classifier=Classifier.STATIC),
        ICAElement(9, "charge_configuration", BitString, classifier=Classifier.STATIC),  # todo make with bit names
        ICAElement(10, "last_collection_time", cst.OctetStringDateTime, classifier=Classifier.DYNAMIC),
        ICAElement(11, "last_collection_amount", DoubleLong, classifier=Classifier.DYNAMIC),
        ICAElement(12, "total_amount_remaining", DoubleLong, classifier=Classifier.DYNAMIC),
        ICAElement(13, "proportion", LongUnsigned, classifier=Classifier.STATIC)
    )
    M_ELEMENTS = (
        ICMElement(1, "update_unit_charge", Array[ChargeTableElement]),
        ICMElement(2, "activate_passive_unit_charge", integers.IntegerValue0),
        ICMElement(3, "collect", integers.IntegerValue0),
        ICMElement(4, "update_total_amount_remaining", DoubleLong),
        ICMElement(5, "set_total_amount_remaining", DoubleLong)
    )
    total_amount_paid: Attr
    charge_type: Attr
    priority: Attr
    unit_charge_active: Attr
    unit_charge_passive: Attr
    unit_charge_activation_time: Attr
    period: Attr
    charge_configuration: Attr
    last_collection_time: Attr
    last_collection_amount: Attr
    total_amount_remaining: Attr
    proportion: Attr
