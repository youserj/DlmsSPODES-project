from typing import Final
from COSEMpdu.data import Enum, Array, Structure, Boolean, OctetString, DoubleLongUnsigned, BitString
from ...types.implementations import integers
from ...types.type_alias import Attr, Meth
from ..cosem_interface_class import ICAElement, ICMElement, ICAuto, Classifier


class ImageTransferStatus(Enum):
    """ Holds the status of the Image transfer process. """
    TRANSFER_NOT_INITIATED: Final = 0
    TRANSFER_INITIATED: Final = 1
    VERIFICATION_INITIATED: Final = 2
    VERIFICATION_SUCCESSFUL: Final = 3
    VERIFICATION_FAILED: Final = 4
    ACTIVATION_INITIATED: Final = 5
    ACTIVATION_SUCCESSFUL: Final = 6
    ACTIVATION_FAILED: Final = 7


class ImageToActivateInfoElement(Structure):
    """image_to_activate_info_element"""
    image_to_activate_size: DoubleLongUnsigned
    image_to_activate_identification: OctetString
    image_to_activate_signature: OctetString


ImageToActivateInfo = Array[ImageToActivateInfoElement]
"""image_to_activate_info attribute"""


class ImageTransferInitiate(Structure):
    """image_transfer_initiate method"""
    image_identifier: OctetString
    image_size: DoubleLongUnsigned


class ImageBlockTransfer(Structure):
    """image_block_transfer method"""
    image_block_number: DoubleLongUnsigned
    image_block_value: OctetString


class ImageTransfer(ICAuto):
    """4.4.6 Image transfer"""
    CLASS_ID = 18
    VERSION = 0
    A_ELEMENTS = (
        ICAElement(2, "image_block_size", DoubleLongUnsigned),
        ICAElement(3, "image_transferred_blocks_status", BitString, classifier=Classifier.DYNAMIC),
        ICAElement(4, "image_first_not_transferred_block_number", DoubleLongUnsigned, classifier=Classifier.DYNAMIC),
        ICAElement(5, "image_transfer_enabled", Boolean),
        ICAElement(6, "image_transfer_status", ImageTransferStatus, classifier=Classifier.DYNAMIC),
        ICAElement(7, "image_to_activate_info", ImageToActivateInfo, classifier=Classifier.DYNAMIC))
    M_ELEMENTS = (
        ICMElement(1, "image_transfer_initiate", ImageTransferInitiate),
        ICMElement(2, "image_block_transfer", ImageBlockTransfer),
        ICMElement(3, "image_verify", integers.IntegerValue0),
        ICMElement(4, "image_activate", integers.IntegerValue0))
    image_block_size: Attr
    image_transferred_blocks_status: Attr
    image_first_not_transferred_block_number: Attr
    image_transfer_enabled: Attr
    image_transfer_status: Attr
    image_to_activate_info: Attr
    image_transfer_initiate: Meth
    image_block_transfer: Meth
    image_verify: Meth
    image_activate: Meth
