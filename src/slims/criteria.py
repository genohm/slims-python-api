import datetime
from enum import Enum


class _JunctionType(Enum):
    AND = 1
    OR = 2
    NOT = 3


class Criterion(object):

    def to_dict(self):
        """ Serializes criterion to dictionary """
        raise NotImplementedError


class Expression(Criterion):
    """ A simple expression like 'cntn_id' equals 'test' """

    def __init__(self, criterion):
        self.criterion = criterion

    def to_dict(self):
        return_value = {}
        for key in self.criterion:
            value = self.criterion[key]
            if isinstance(value, datetime.datetime):
                return_value[key] = value.isoformat()
            else:
                return_value[key] = value
        return return_value


class Junction(Criterion):
    """ A combination of multiple criteria """

    def __init__(self, operator):
        self.operator = operator
        self.members = []

    def add(self, member):
        """ Adds a member to this junction """
        self.members.append(member)
        return self

    def to_dict(self):
        member_dicts = []
        for member in self.members:
            member_dicts.append(member.to_dict())
        return {
            "operator": self.operator.name.lower(),
            "criteria": member_dicts
        }


def equals(field, value):
    """Applies an "equals" constraint to the specified field

    This is case-sensitive depending on the used database.

    Args:
        field (string): the field to match
        value (any): the value to match

    Returns:
        An equals criterion

    Examples:
        >>> slims.fetch("Content", equals("cntn_id", "dna0001"))

        This will fetch all the content records that have "dna0001" as their id
    """
    return Expression(_criterion(field, "equals", value))


def equals_ignore_case(field, value):
    """Applies an "equals" constraint to the specified field

    This is always case-insensitive

    Args:
        field (string): the field to match
        value (any): the value to match

    Returns:
        An equals criterion

    Examples:
        >>> slims.fetch("Content", equals_ignore_case("cntn_id", "dna0001"))

        Will fetch all the content records that have "dna0001" as their id
    """
    return Expression(_criterion(field, "iEquals", value))


# Could be done by using the equals function and the NOT junction
def not_equals(field, value):
    """Applies an "not equals" constraint to the specified field

    Args:
        field (string): the field to match
        value (any): the value not to match

    Returns:
        A not equals criterion

    Examples:
        >>> slims.fetch("Content", not_equals("cntn_id", "dna0001"))

        Will fetch all the content records that do not have "dna0001" as their id
    """
    return Expression(_criterion(field, "iNotEqual", value))


def is_null(field):
    """Applies an "is null" constraint to the specified field

    Args:
        field (string): the field that should be null

    Returns:
        An is null criterion

    Examples:
        >>> slims.fetch("Content", is_null("cntn_fk_location"))

        Will fetch all the content records that are not in a location
    """
    return Expression(_criterion(field, "isNull", None))


# Could be done by using the isNull function and the NOT junction
def is_not_null(field):
    """Applies an "is not null" constraint to the specified field

    Args:
        field (string): the field that shouldn't be null

    Returns:
        A not null criterion

    Examples:
        >>> slims.fetch("Content", is_not_null("cntn_fk_location"))

        Will fetch all the content records that are in a location
    """
    return Expression(_criterion(field, "notNull", None))


def starts_with(field, value):
    """Applies a "starts with" constraint to the specified field

    Args:
        field (string): the field to match
        value (any): the value to start with

    Returns:
        A starts with criterion

    Examples:
        >>> slims.fetch("Content", start_with("cntn_id", "dna"))

        Will fetch all the content records that have an id that starts with "dna"
    """
    return Expression(_criterion(field, "iStartsWith", value))


def ends_with(field, value):
    """Applies an "ends with" constraint to the specified field

    Args:
        field (string): the field to match
        value (any): the value to end with

    Returns:
        An ends with criterion

    Examples:
        >>> slims.fetch("Content", ends_with("cntn_id", "001"))

        Will fetch all the content records that have an id that ends with "001"
    """
    return Expression(_criterion(field, "iEndsWith", value))


def contains(field, value):
    """Applies a "contains" constraint to the specified field

    Args:
        field (string): the field to match
        value (any): the value to contain

    Returns:
        A contains criterion

    Examples:
        >>> slims.fetch("Content", contains("cntn_id", "test"))

        Will fetch all the content records that have an id that contains "test"
    """
    return Expression(_criterion(field, "iContains", value))


# For now, not defined in SLims
def between_inclusive(field, start, end):
    """Applies a "between" constraint to the specified field

    Args:
        field (string): the field to match
        start (any): the value to start with (inclusive)
        start (any): the value to end with (inclusive)

    Returns:
        A between criterion

    Examples:
        >>> slims.fetch("Content", between_inclusive("cntn_barCode", "00001", "00010"))

        Will fetch all the content records that have a barcode between 00001 and 00010
    """
    return Expression(_criterionBetween(field, "betweenInclusive", start, end))


def is_one_of(field, value):
    """Applies an "is one of" constraint to the specified field

    Args:
        field (string)-- the field to match
        value (list)-- the list of values to match

    Examples:
        >>> slims.fetch("Content", is_one_of("cntn_barCode", ["0001", "0002", "0004"]))

        Will fetch all the content records that have a barcode that is either
        0001, 0002 or 0004.
    """
    return Expression(_criterion(field, "inSet", value))


# Could be done by using the isOneOf function and the NOT junction
def is_not_one_of(field, value):
    """Applies an "is not one of" constraint to the specified field

    Args:
        field (string)-- the field to match
        value (list)-- the list of values to not match

    Examples:
        >>> slims.fetch("Content", is_not_one_of("cntn_barCode", ["0001", "0002", "0004"]))

        Will fetch all the content records that have a barcode that is not
        0001, 0002 or 0004.
    """
    return Expression(_criterion(field, "notInSet", value))


def less_than(field, value):
    """Applies an "less than" constraint to the specified field

    Args:
        field (string): the field to match
        value (any): the value to match

    Returns:
        A less than criterion

    Examples:
        >>> slims.fetch("Content", less_than("cntn_quantity", "5"))

        Will fetch all the content records that have a quantity smaller than 5
    """
    return Expression(_criterion(field, "lessThan", value))


def greater_than(field, value):
    """Applies an "greater than" constraint to the specified field

    Args:
        field (string): the field to match
        value (any): the value to match

    Returns:
        A greater than criterion

    Examples:
        >>> slims.fetch("Content", greater_than("cntn_quantity", "5"))

        Will fetch all the content records that have a quantity greater than 5
    """
    return Expression(_criterion(field, "greaterThan", value))


def less_than_or_equal(field, value):
    """Applies an "less than or equal" constraint to the specified field

    Args:
        field (string): the field to match
        value (any): the value to match

    Returns:
        A less than or equal criterion

    Examples:
        >>> slims.fetch("Content", less_than_or_equal("cntn_quantity", "5"))

        Will fetch all the content records that have a quantity less than or
        equal to 5
    """
    return Expression(_criterion(field, "lessOrEqual", value))


def greater_than_or_equal(field, value):
    """Applies an "greater than or equal" constraint to the specified field

    Args:
        field (string): the field to match
        value (any): the value to match

    Returns:
        A less than or equal criterion

    Examples:
        >>> slims.fetch("Content", greater_than_or_equal("cntn_quantity", "5"))

        Will fetch all the content records that have a quantity greater than or
        equal to 5
    """
    return Expression(_criterion(field, "greaterOrEqual", value))


def is_na(field):
    """Applies a "is not applicable" constraint to the specified field (this is an
    option on custom fields

    Args:
        field (string): the field that should not be applicable

    Returns:
        A not applicable criterion

    Examples:
        >>> slims.fetch("Content", is_na("cntn_cf_numberOfSigarettes"))

        Will fetch all the content records for which the number of sigarrettes
        is not applible (for example for non smokers)
    """
    return Expression(_criterion("isNaFilter", "equals", field))


def _criterion(field, operator, value=None):
    return_value = {
        "fieldName": field,
        "operator": operator
    }
    if value:
        return_value["value"] = value
    return return_value


def _criterionBetween(field, operator, start, end):
    return_value = {
        "fieldName": field,
        "operator": operator,
        "start": start,
        "end": end,
    }
    return return_value


def conjunction():
    """Combines multiple criteria in a conjunctive way (and)

    Returns:
        A conjunction

    Examples:
        >>> slims.fetch("Content", conjunction()
                    .add(start_with("cntn_id", "DNA"))
                    .add(greater_than("cntn_quantity", 5)

        Will fetch all the content records for which their id starts with
        "DNA" and their quantity is bigger than 5.
    """
    return Junction(_JunctionType.AND)


def disjunction():
    """Combines multiple criteria in a disjunctive way (or)

    Returns:
        A disjunction

    Examples:
        >>> slims.fetch("Content", disjunction()
                    .add(start_with("cntn_id", "DNA"))
                    .add(greater_than("cntn_quantity", 5)

        Will fetch all the content records for which their id starts with
        "DNA" or their quantity is bigger than 5.
    """
    return Junction(_JunctionType.OR)


def is_not(criterion):
    """Inverts a criterion

    Args:
        criterion (criterion): The criterion to invert

    Returns:
        A criterion

    Examples:
        >>> slims.fetch("Content", is_not(start_with("cntn_id", "DNA")))

        Will fetch all the content records for which their id does not
        starts with "DNA"
    """
    return Junction(_JunctionType.NOT).add(criterion)
