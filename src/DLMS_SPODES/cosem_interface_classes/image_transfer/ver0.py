from ..__class_init__ import *
from ...types.implementations import integers
from . image_transfer_status import ImageTransferStatus
from ..overview import VERSION_0


class ImageToActivateInfoElement(cdt.Structure):
    image_to_activate_size: cdt.DoubleLongUnsigned
    image_to_activate_identification: cdt.OctetString
    image_to_activate_signature: cdt.OctetString


class ImageToActivateInfo(cdt.Array):
    """ Provides information on the Image(s) ready for activation. It is generated as the result of the Image verification process. Thi client may check this information before
    activating the Images. """
    TYPE = ImageToActivateInfoElement
    __getitem__: ImageToActivateInfoElement


class ImageTransferInitiate(cdt.Structure):
    """ Initializes the Image transfer process. After a successful invocation of the method the image_transfer_status attribute is set to (1) and the
    image_first_not_transferred_block_number is set to 0. Any subsequent invocation of the method resets the whole Image transfer process and all ImageBlocks need to be
    transferred again. """
    DEFAULT = (bytearray(b'default'), 0)
    image_identifier: cdt.OctetString
    image_size: cdt.DoubleLongUnsigned


class ImageBlockTransfer(cdt.Structure):
    """ Transfers one block of the Image to the server. After a successful invocation of the method the corresponding bit in the image_transferred_block_status attribute
    is set to 1 and the image_first_bit_transferred_block_number attribute is updated """
    image_block_number: cdt.DoubleLongUnsigned
    image_block_value: cdt.OctetString


class ImageTransfer(ic.COSEMInterfaceClasses):
    """ Instance of the Image transfer IC model the process of transferring binary files, called Images to COSEM servers. """
    CLASS_ID = ClassID.IMAGE_TRANSFER
    VERSION = VERSION_0
    __blocks_for_update: list[bytearray]
    A_ELEMENTS = (ic.ICAElement(2, "image_block_size", cdt.DoubleLongUnsigned),
                  ic.ICAElement(3, "image_transferred_blocks_status", cdt.BitString, classifier=ic.Classifier.DYNAMIC),
                  ic.ICAElement(4, "image_first_not_transferred_block_number", cdt.DoubleLongUnsigned, classifier=ic.Classifier.DYNAMIC),
                  ic.ICAElement(5, "image_transfer_enabled", cdt.Boolean),
                  ic.ICAElement(6, "image_transfer_status", ImageTransferStatus, classifier=ic.Classifier.DYNAMIC),
                  ic.ICAElement(7, "image_to_activate_info", ImageToActivateInfo, classifier=ic.Classifier.DYNAMIC))
    M_ELEMENTS = (ic.ICMElement(1, "image_transfer_initiate", ImageTransferInitiate),
                  ic.ICMElement(2, "image_block_transfer", ImageBlockTransfer),
                  ic.ICMElement(3, "image_verify", integers.INTEGER_0),
                  ic.ICMElement(4, "image_activate", integers.INTEGER_0))

    def characteristics_init(self):
        # TODO: compare image_block_size with ServerMaxReceive
        self.__blocks_for_update = list()
        """ container of blocks for transfer """

    @property
    def image_block_size(self) -> cdt.DoubleLongUnsigned:
        return self.get_attr(2)

    @property
    def image_transferred_blocks_status(self) -> cdt.BitString:
        return self.get_attr(3)

    @property
    def image_first_not_transferred_block_number(self) -> cdt.DoubleLongUnsigned:
        return self.get_attr(4)

    @property
    def image_transfer_enabled(self) -> cdt.Boolean:
        return self.get_attr(5)

    @property
    def image_transfer_status(self) -> ImageTransferStatus:
        return self.get_attr(6)

    @property
    def image_to_activate_info(self) -> ImageToActivateInfo:
        return self.get_attr(7)

    @property
    def current_block_transfer(self) -> int:
        return int(self.image_block_transfer.image_block_number)

    def get_n_blocks(self) -> int:
        """get sum of blocks"""
        return len(self.__blocks_for_update)

    def set_next_block(self):
        """ set next block transfer """
        try:
            # TODO: USE bitstring of BlockStatus if it exist(length order by image) for pretty next block
            self.set_block_for_transfer(self.current_block_transfer+1)
        except IndexError:
            raise StopIteration

    def set_block_for_transfer(self, index: int):
        """ set block transfer number. IndexError if index more when blocks size """
        if index > (len(self.__blocks_for_update) - 1):
            raise IndexError(F"got block {index=}, expected 0..{len(self.__blocks_for_update)-1}")
        self.image_block_transfer.set((index, self.__blocks_for_update[index]))

    @property
    def is_image_exist(self) -> bool:
        """ show is existing image in container """
        return bool(len(self.__blocks_for_update))

    def clear_image(self):
        """ clear image container """
        self.__blocks_for_update.clear()
