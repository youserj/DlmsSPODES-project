from .__class_init__ import *
from ..types.implementations import integers


TRANSFER_NOT_INITIATED = 0
TRANSFER_INITIATED = 1
VERIFICATION_INITIATED = 2
VERIFICATION_SUCCESSFUL = 3
VERIFICATION_FAILED = 4
ACTIVATION_INITIATED = 5
ACTIVATION_SUCCESSFUL = 6
ACTIVATION_FAILED = 7


class ImageTransferStatus(cdt.Enum, elements=tuple(range(8))):
    """ Holds the status of the Image transfer process. """


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
    default = (bytearray(b'default'), 0)
    image_identifier: cdt.OctetString
    image_size: cdt.DoubleLongUnsigned


class ImageBlockTransfer(cdt.Structure):
    """ Transfers one block of the Image to the server. After a successful invocation of the method the corresponding bit in the image_transferred_block_status attribute
    is set to 1 and the image_first_bit_transferred_block_number attribute is updated """
    image_block_number: cdt.DoubleLongUnsigned
    image_block_value: cdt.OctetString


class ImageTransfer(ic.COSEMInterfaceClasses):
    """ Instance of the Image transfer IC model the process of transferring binary files, called Images to COSEM servers. """
    NAME = cn.IMAGE_TRANSFER
    CLASS_ID = ClassID.IMAGE_TRANSFER
    VERSION = Version.V0
    __blocks_for_update: list[bytearray]
    A_ELEMENTS = (ic.ICAElement(an.IMAGE_BLOCK_SIZE, cdt.DoubleLongUnsigned),
                  ic.ICAElement(an.IMAGE_TRANSFERRED_BLOCKS_STATUS, cdt.BitString),
                  ic.ICAElement(an.IMAGE_FIRST_NOT_TRANSFERRED_BLOCK_NUMBER, cdt.DoubleLongUnsigned),
                  ic.ICAElement(an.IMAGE_TRANSFER_ENABLED, cdt.Boolean),
                  ic.ICAElement(an.IMAGE_TRANSFER_STATUS, ImageTransferStatus),
                  ic.ICAElement(an.IMAGE_TO_ACTIVATE_INFO, ImageToActivateInfo))
    M_ELEMENTS = (ic.ICMElement(mn.IMAGE_TRANSFER_INITIATE, ImageTransferInitiate),
                  ic.ICMElement(mn.IMAGE_BLOCK_TRANSFER, ImageBlockTransfer),
                  ic.ICMElement(mn.IMAGE_VERIFY, integers.Only0),
                  ic.ICMElement(mn.IMAGE_ACTIVATE, integers.Only0))

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
    def image_transfer_initiate(self) -> ImageTransferInitiate:
        return self.get_meth(1)

    @property
    def image_block_transfer(self) -> ImageBlockTransfer:
        return self.get_meth(2)

    @property
    def image_verify(self) -> integers.Only0:
        return self.get_meth(3)

    @property
    def image_activate(self) -> integers.Only0:
        return self.get_meth(4)

    def set_image_for_update(self, value: bytes, identifier: bytearray):
        """ set to image_for_update from bytes and set to first block if identifier is new """
        block_size: int = self.image_block_size.decode()
        self.clear_image()
        while len(value) != 0:
            self.__blocks_for_update.append(bytearray(value[:block_size]))
            value = value[block_size:]
        if bytes(identifier) != self.image_transfer_initiate.image_identifier.contents:
            self.image_transfer_initiate.image_identifier.set(identifier)
            self.image_block_transfer.image_block_number.set(0)
        elif self.current_block_transfer == 0:
            pass
        elif self.current_block_transfer >= len(self.__blocks_for_update):
            self.image_block_transfer.image_block_number.set(0)
        else:
            self.image_block_transfer.image_block_number.set(self.current_block_transfer - 1)
        self.image_transfer_initiate.image_size.set(sum(map(len, self.__blocks_for_update)))
        self.image_block_transfer.image_block_value.set(self.__blocks_for_update[self.current_block_transfer])

    @property
    def sent_blocks_part(self) -> float:
        """ return part of sent block if available else 0 """
        if len(self.__blocks_for_update) != 0:
            return self.image_block_transfer.image_block_number.decode() / len(self.__blocks_for_update)
        else:
            return 0

    @property
    def current_block_transfer(self) -> int:
        return int(self.image_block_transfer.image_block_number)

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
        self.image_block_transfer.image_block_value.set(self.__blocks_for_update[index])
        self.image_block_transfer.image_block_number.set(index)

    @property
    def is_image_exist(self) -> bool:
        """ show is existing image in container """
        return bool(len(self.__blocks_for_update))

    def clear_image(self):
        """ clear image container """
        self.__blocks_for_update.clear()


if __name__ == '__main__':
    c = ImageToActivateInfo()
    c.set([[1, '00', '11']])
    a = ImageTransferInitiate(['00', 0])
    a.set(['11', 1])
    a = ImageTransferStatus()
    print(a == ImageTransferStatus('Image transfer not initiated'))
    match a:
        case ImageTransferStatus('Image transfer not initiated'): print(a)
    # print(a == 27)
