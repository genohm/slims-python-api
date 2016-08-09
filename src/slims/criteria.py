import datetime
from enum import Enum


class JunctionType(Enum):
    AND = 1
    OR = 2
    NOT = 3


class Criterion(object):

    def to_dict(self):
        raise NotImplementedError


class Expression(Criterion):

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

    def __init__(self, operator):
        self.operator = operator
        self.members = []

    def add(self, member):
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
    """Allows to select elements regarding a field that equal a certain value.

    It differentiates the capital from non-capital letters.
    Parameters:
    field -- the field that need to be evaluated
    value -- the value to which the field needs to be equal

    Returns: the elements with the field equal to a specific value
    """
    return Expression(_criterion(field, "equals", value))


def equals_ignore_case(field, value):
    """Allows to select elements regarding a field that equal a certain value.

    It does not differentiate the capital from non-capital letters.
    Parameters:
    field -- the field that need to be evaluated
    value -- the value to which the field needs to be equal

    Returns: the elements with the field equal to a specific value
    """
    return Expression(_criterion(field, "iEquals", value))


# Could be done by using the equals function and the NOT junction
def not_equals(field, value):
    """Allows to select elements regarding a field that does not equal a value.

    It does not differentiate the capital from non-capital letters.
    Parameters:
    field -- the field that need to be evaluated
    value -- the value to which the field must not be equal

    Returns: the elements with the field not equal to a specific value
    """
    return Expression(_criterion(field, "iNotEqual", value))


def is_null(field):
    """Allows to select elements regarding a field that equal NULL.

    Parameters:
    field -- the field that need to be evaluated

    Returns: the elements with the field equal to NULL
    """
    return Expression(_criterion(field, "isNull", None))


# Could be done by using the isNull function and the NOT junction
def is_not_null(field):
    """Allows to select elements regarding a field that does not equal NULL.

    Parameters:
    field -- the field that need to be evaluated

    Returns: the elements with the field not equal to NULL
    """
    return Expression(_criterion(field, "notNull", None))


def starts_with(field, value):
    """Allows to select elements regarding a field that starts with certain value.

    Parameters:
    field -- the field that need to be evaluated
    value -- the value with which the field needs to start

    Returns: the elements with the field starting with the value
    """
    return Expression(_criterion(field, "iStartsWith", value))


def ends_with(field, value):
    """Allows to select elements regarding a field that ends with certain value.

    Parameters:
    field -- the field that need to be evaluated
    value -- the value with which the field needs to end

    Returns: the elements with the field ending with the value
    """
    return Expression(_criterion(field, "iEndsWith", value))


def contains(field, value):
    """Allows to select elements regarding a field that contains a certain value.

    Parameters:
    field -- the field that need to be evaluated
    value -- the value that need to be contained by the field

    Returns: the elements with the field containing the value
    """
    return Expression(_criterion(field, "iContains", value))


# For now, not defined in SLims
def between_inclusive(field, start, end):
    return Expression(_criterionBetween(field, "betweenInclusive", start, end))


def between_inclusive_match_case(field, start, end):
    """Allows to select elements regarding a field that is betweem two values.

    It differentiates the capital from non-capital letters.
    Parameters:
    field -- the field that need to be evaluated
    start -- the lower value of the bound
    end -- the upper value of the bound

    Returns: the elements with the field comprise in between the two values
    """
    return Expression(_criterionBetween(field, "betweenInclusive", start, end))


def is_one_of(field, value):
    """Allows to select a specific set of elements based on the field.

    Parameters:
    field -- the field that need to be checked
    value -- the set ([]) of value that needs to be selected

    Returns: the elements that coincide with the given value(s)
    """
    return Expression(_criterion(field, "inSet", value))


# Could be done by using the isOneOf function and the NOT junction
def is_not_one_of(field, value):
    """Allows to exclue elements from the final set based on the field.

    Parameters:
    field -- the field that need to be checked
    value -- the set ([]) of value that needs to be exclued

    Returns: the elements that are not given as value
    """
    return Expression(_criterion(field, "notInSet", value))


def less_than(field, value):
    """Allows to select elements with a field less than a value.
    Parameters:
    field -- the field that needs to be less than
    value -- the value that serves as limit

    Returns: the elements having the field less than a value
    """
    return Expression(_criterion(field, "lessThan", value))


def greater_than(field, value):
    """Allows to select elements with a field greater than a value.

    Parameters:
    field -- the field that needs to be greater than
    value -- the value that serves as limit

    Returns: the elements having the field greater than a value
    """
    return Expression(_criterion(field, "greaterThan", value))


def less_than_or_equal(field, value):
    """Allows to select elements with a field less than or equal to a value.
    Parameters:
    field -- the field that needs to be less than or equal
    value -- the value that serves as limit

    Returns: the elements having the field less than or equal to a value
    """
    return Expression(_criterion(field, "lessOrEqual", value))


def greater_than_or_equal(field, value):
    """Allows to select elements with a field greater than or equal to a value.

    Parameters:
    field -- the field that needs to be greater than or equal
    value -- the value that serves as limit

    Returns: the elements having the field greater than or equal to a value
    """
    return Expression(_criterion(field, "greaterOrEqual", value))


def is_na(field):
    """Allows to select the elements having a field with a NA.

    Parameter:
    field -- the field that can take NA as value

    Returns: the elements having a field with a NA
    """
    return Expression(_criterion("isNaFilter", "equals", field))


def _criterion(field, operator, value=None):
    """Defines the necessary information for the functions of operators.

    Parameters:
    field -- the field on which the operator needs to be applied
    operator -- the operator displayed in the SmartClient Developer Console
    value -- the value demanded by the operator
             default value is None but can also be multiple (list)

    Returns: the necessary information for the function of operator
    """
    return_value = {
        "fieldName": field,
        "operator": operator
    }
    if value:
        return_value["value"] = value
    return return_value


def _criterionBetween(field, operator, start, end):
    """Defines the necessary information for the functions of between operators.

    Parameters:
    field -- the field on which the operator needs to be applied
    operator -- the operator displayed in the SmartClient Developer Console
    start -- the lowest value demanded by the operator between
    end -- the highest value demanded by the operator between

    Retruns: the necessary information for the function of operator
    """
    return_value = {
        "fieldName": field,
        "operator": operator,
        "start": start,
        "end": end,
    }
    return return_value


def conjunction():
    """Allows to informatio operations in a additive way (and)."""
    return Junction(JunctionType.AND)


def disjunction():
    """Allows to join operations with alternatives (or)."""
    return Junction(JunctionType.OR)


def is_not(criterion):
    """Allows to join operations in a substractive way (not).

    Paramters:
    criterion -- the wanted criteria used in the substractive operator
    """
    return Junction(JunctionType.NOT).add(criterion)
