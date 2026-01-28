from ...types.implementations import integers
from . image_transfer_status import ImageTransferStatus
from ...types import cdt
from ...types.type_alias import Attr, Meth
from ..cosem_interface_class import ICAElement, ICMElement, ICAuto, Classifier
from ..Overview import class_id


class ImageToActivateInfoElement(cdt.Structure):
    """image_to_activate_info_element"""
    image_to_activate_size: cdt.DoubleLongUnsigned
    image_to_activate_identification: cdt.OctetString
    image_to_activate_signature: cdt.OctetString


class ImageToActivateInfo(cdt.Array):
    """image_to_activate_info attribute"""
    TYPE = ImageToActivateInfoElement
    __getitem__: ImageToActivateInfoElement


class ImageTransferInitiate(cdt.Structure):
    """image_transfer_initiate method"""
    image_identifier: cdt.OctetString
    image_size: cdt.DoubleLongUnsigned


class ImageBlockTransfer(cdt.Structure):
    """image_block_transfer method"""
    image_block_number: cdt.DoubleLongUnsigned
    image_block_value: cdt.OctetString


class ImageTransfer(ICAuto):
    """4.4.6 Image transfer"""
    CLASS_ID = class_id.IMAGE_TRANSFER
    VERSION = 0
    A_ELEMENTS = (ICAElement(2, "image_block_size", cdt.DoubleLongUnsigned),
                  ICAElement(3, "image_transferred_blocks_status", cdt.BitString, classifier=Classifier.DYNAMIC),
                  ICAElement(4, "image_first_not_transferred_block_number", cdt.DoubleLongUnsigned, classifier=Classifier.DYNAMIC),
                  ICAElement(5, "image_transfer_enabled", cdt.Boolean),
                  ICAElement(6, "image_transfer_status", ImageTransferStatus, classifier=Classifier.DYNAMIC),
                  ICAElement(7, "image_to_activate_info", ImageToActivateInfo, classifier=Classifier.DYNAMIC))
    M_ELEMENTS = (ICMElement(1, "image_transfer_initiate", ImageTransferInitiate),
                  ICMElement(2, "image_block_transfer", ImageBlockTransfer),
                  ICMElement(3, "image_verify", integers.Only0),
                  ICMElement(4, "image_activate", integers.Only0))
    image_block_size: Attr
    image_transferred_blocks_status: Attr
    image_first_not_transferred_block_number: Attr
    image_transfer_enabled: Attr
    image_transfer_status: Attr
    image_to_activate_info: Attr
    image_transfer_initiate : Meth
    image_block_transfer: Meth
    image_verify: Meth
    image_activate: Meth
