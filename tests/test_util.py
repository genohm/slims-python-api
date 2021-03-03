import datetime
import sys
import unittest
from contextlib import contextmanager
from io import StringIO

from slims.internal import Record
from slims.util import display_field_value


@contextmanager
def redirect_stdout(new_target):
    """
    this code will intercept the print method and send it to the method's argument (a stream-like object)
    below, we use a StringIO so that the print output can end up in a string variable
    see https://stackoverflow.com/a/22434262/2065017
    """
    old_target, sys.stdout = sys.stdout, new_target  # replace sys.stdout
    try:
        yield new_target  # run some code with the replaced stdout
    finally:
        sys.stdout = old_target  # restore to the previous value


class Test_Util(unittest.TestCase):

    def test_display_field_value_quantity_values(self):
        content = {
            "columns": [
                {"name": "cntn_quantity1", "datatype": "QUANTITY", "unit": None, "value": None},
                {"name": "cntn_quantity2", "datatype": "QUANTITY", "unit": "kJ", "value": 4.184},
                {"name": "cntn_quantity3", "datatype": "QUANTITY", "unit": "mm", "value": None},
                {"name": "cntn_quantity4", "datatype": "QUANTITY", "unit": None, "value": 6.02214076e23}
                ]
        }
        rec = Record(content, None)

        stringStream = StringIO()
        with redirect_stdout(stringStream):
            display_field_value(rec, ["cntn_quantity1", "cntn_quantity2", "cntn_quantity3", "cntn_quantity4"])

        self.assertEquals(stringStream.getvalue().strip(), "None None 4.184 kJ None mm 6.02214076e+23 None")

    def test_display_field_value_date_values(self):
        content = {
            "columns": [
                {"name": "cntn_datetime", "datatype": "DATE", "subType": "datetime", "value": 1610000000000},
                {"name": "cntn_date", "datatype": "DATE", "subType": "date", "value": 1602000000000},
                {"name": "cntn_time", "datatype": "DATE", "subType": "time", "value": 36360000}]
        }
        rec = Record(content, None)
        # must be converted with the same timezone as the code that is being tested
        datetimevalue = datetime.datetime.fromtimestamp(content["columns"][0]["value"] / 1000.0)

        stringStream = StringIO()
        with redirect_stdout(stringStream):
            display_field_value(rec, ["cntn_datetime", "cntn_date", "cntn_time"])

        self.assertEquals(stringStream.getvalue().strip(), str(datetimevalue) + " 2020-10-06 10:06")

    def test_display_field_value_date_nones(self):
        content = {
            "columns": [
                {"name": "cntn_datetime", "datatype": "DATE", "subType": "datetime", "value": None},
                {"name": "cntn_date", "datatype": "DATE", "subType": "date", "value": None},
                {"name": "cntn_time", "datatype": "DATE", "subType": "time", "value": None}]
        }
        rec = Record(content, None)

        stringStream = StringIO()
        with redirect_stdout(stringStream):
            display_field_value(rec, ["cntn_datetime", "cntn_date", "cntn_time"])

        self.assertEquals(stringStream.getvalue().strip(), "None None None")
