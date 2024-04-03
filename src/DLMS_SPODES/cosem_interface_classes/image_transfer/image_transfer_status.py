from ...types import cdt


class ImageTransferStatus(cdt.Enum, elements=tuple(range(8))):
    """ Holds the status of the Image transfer process. """


TRANSFER_NOT_INITIATED = ImageTransferStatus(0)
TRANSFER_INITIATED = ImageTransferStatus(1)
VERIFICATION_INITIATED = ImageTransferStatus(2)
VERIFICATION_SUCCESSFUL = ImageTransferStatus(3)
VERIFICATION_FAILED = ImageTransferStatus(4)
ACTIVATION_INITIATED = ImageTransferStatus(5)
ACTIVATION_SUCCESSFUL = ImageTransferStatus(6)
ACTIVATION_FAILED = ImageTransferStatus(7)
