from __future__ import print_function
import datetime
import time


def display_results(records, fields, number=None):
    """Allows to display the filtered results.

    Parameters:
    records -- the results to displayed
    fields -- the fields to displayed
              it needs to be a list of string (["field"] or ["field1", "field2"])
    number -- the number of displayed results
               default value is None which displayed all existing results

    Returns: a list of elements with their selected fields
    """

    print(' '.join(fields))
    if number is None or number >= len(records):
        for record in records:
            display_field_value(record, fields)
    else:
        print("Number of displayed results: " + str(number) + '\n')
        for record in records[:number]:
            display_field_value(record, fields)
    return None


def display_field_value(record, fields):
    """Allows to display the results depending on the field.

    Parameters:
    records -- the results to displayed
    fields -- the fields to displayed
              it needs to be a list of string (["field"] or ["field1", "field2"])

    Returns: the print of the results
    """

    for field in fields:
        if record.column(field).datatype in "QUANTITY":
            print(record.column(field).value, end=" ")
            print(record.column(field).unit, end=" ")
        elif record.column(field).datatype in "DATE":
            if record.column(field).subType in "date":
                print(datetime.date.fromtimestamp(record.column(field).value / 1000.0), end=" ")
            elif record.column(field).subType in "datetime":
                print(datetime.datetime.fromtimestamp(record.column(field).value / 1000.0), end=" ")
            else:
                print(time.strftime("%H:%M", time.localtime(int(record.column(field).value)/1000)), end=" ")
        else:
            print(record.column(field).value, end=" ")
    print(end='\n',)
