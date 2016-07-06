from enum import Enum


class JunctionType(Enum):
    AND = 1
    OR = 2


class Criterion(object):

    def to_dict(self):
        raise NotImplementedError


class Expression(Criterion):

    def __init__(self, criterion):
        self.criterion = criterion

    def to_dict(self):
        return self.criterion


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
    return Expression(_criterion(field, "equals", value))


def conjunction():
    return Junction(JunctionType.AND)


def disjunction():
    return Junction(JunctionType.OR)


def _criterion(field, operator, value=None):
    return_value = {
        "fieldName": field,
        "operator": operator
    }
    if value:
        return_value["value"] = value
    return return_value
