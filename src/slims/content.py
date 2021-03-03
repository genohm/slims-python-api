from enum import Enum

from deprecation import deprecated


@deprecated(details="""Enum-value statuses are deprecated since SLIMS 6.4.
            Unless your SLIMS system still uses them (see Lab Settings),
            you should use the Status table and cntn_fk_status for status queries.""")
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
