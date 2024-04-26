from dataclasses import dataclass


@dataclass
class Priority:
    value: bool

    def __str__(self):
        return "High" if self.value else "Normal"

    def __int__(self):
        return 0b1000_0000 if self.value else 0


NORMAL = Priority(False)
HIGH = Priority(True)
