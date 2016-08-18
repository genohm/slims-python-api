from enum import Enum


class Status(Enum):
    PENDING = 10
    AVAILABLE = 20
    LABELED = 30
    APPROVED = 40
    REMOVED = 50
    CANCELLED = 60
