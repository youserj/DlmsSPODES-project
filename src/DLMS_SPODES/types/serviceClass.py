from dataclasses import dataclass


@dataclass
class ServiceClass:
    value: bool

    def __str__(self):
        return "Confirmed" if self.value else "Unconfirmed"

    def __int__(self):
        return 0b0100_0000 if self.value else 0


UNCONFIRMED = ServiceClass(False)
CONFIRMED = ServiceClass(True)
