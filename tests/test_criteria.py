import unittest

from slims.criteria import between_inclusive
from slims.criteria import conjunction
from slims.criteria import equals
from slims.criteria import is_one_of
from slims.criteria import is_not
from slims.criteria import starts_with


class Test_Criteria(unittest.TestCase):

    def test_simple_equals(self):
        expected = {"fieldName": "cntn_id", "operator": "equals", "value": "test"}
        self.assertEqual(expected, equals("cntn_id", "test").to_dict())

    def test_in(self):
        expected = {"fieldName": "cntn_id", "operator": "inSet", "value": ["a", "b", "c"]}
        self.assertEqual(expected, is_one_of("cntn_id", ["a", "b", "c"]).to_dict())

    def test_between(self):
        expected = {"fieldName": "cntn_id", "operator": "betweenInclusive", "start": 1, "end": 2}
        self.assertEqual(expected, between_inclusive("cntn_id", 1, 2).to_dict())

    def test_conjunction(self):
        expected = {"operator": "and",
                    "criteria": [
                        {"fieldName": "cntn_id", "operator": "equals", "value": "test"},
                        {"fieldName": "cntn_barCode", "operator": "iStartsWith", "value": "blah"},
                    ]}
        criteria = conjunction().add(equals("cntn_id", "test")).add(starts_with("cntn_barCode", "blah"))
        self.assertEqual(expected, criteria.to_dict())

    def test_not(self):
        expected = {"operator": "not",
                    "criteria": [
                        {"fieldName": "cntn_id", "operator": "equals", "value": "test"},
                    ]}

        criteria = is_not(equals("cntn_id", "test"))
        self.assertEqual(expected, criteria.to_dict())
