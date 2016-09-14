from enum import Enum


class Status(Enum):
    """List of content statusses in SLims

    Can be used to fetch or update content

    Examples:
        >>> slims.fetch("Content",
                equals("cntn_status", Status.PENDING.value))
    """

    PENDING = 10
    AVAILABLE = 20
    LABELED = 30
    APPROVED = 40
    REMOVED = 50
    CANCELLED = 60
