import unittest

from slims.step import single_choice_with_field_list_input
from slims.step import single_choice_with_value_map_input
from slims.step import text_input


class Test_Slimsgate_Input(unittest.TestCase):

    def test_type_input(self):
        expected = {"label": "Label", "name": "name", "type": "STRING"}
        self.assertDictEqual(expected, text_input("name", "Label"))

    def test_type_input_with_default_value(self):
        expected = {"label": "Label", "name": "name", "type": "STRING", "defaultValue": "test"}
        self.assertDictEqual(expected, text_input("name", "Label", defaultValue="test"))

    def test_single_choice_with_field_list_input_and_types(self):
        values = single_choice_with_field_list_input(
            "choice",
            "Choice",
            ["Hi", "Good Morning", "Hello"],
            ["String", "String", "String"])

        expected = {"name": "choice", "label": "Choice", "type": "SINGLE_CHOICE",
                    "fieldList": {
                        "entries": [
                            {'field': 'Hi', 'type': 'String'},
                            {'field': 'Good Morning', 'type': 'String'},
                            {'field': 'Hello', 'type': 'String'}
                        ]
                    }}
        self.assertDictEqual(expected, values)

    def test_single_choice_with_field_list_input_without_types(self):
        values = single_choice_with_field_list_input(
            "choice",
            "Choice",
            ["Hi"])

        expected = {"name": "choice", "label": "Choice", "type": "SINGLE_CHOICE",
                    "fieldList": {
                        "entries": [
                            {'field': 'Hi', 'type': None}
                        ]
                    }}
        self.assertDictEqual(expected, values)

    def test_single_choice_with_value_map_input(self):
        values = single_choice_with_value_map_input(
            "choice",
            "Choice",
            table="Content",
            reference="reference",
            filtered="filter",
            fixed_choice_custom_field="cntn_cf_test")

        expected = {"name": "choice", "label": "Choice", "type": "SINGLE_CHOICE",
                    "valueMap": {
                        'filter': 'filter',
                        'fixedChoiceCustomField': 'cntn_cf_test',
                        'reference': 'reference',
                        'table': 'Content'
                    }}
        self.assertDictEqual(expected, values)
