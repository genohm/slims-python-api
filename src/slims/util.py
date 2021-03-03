import datetime
import time

from .slims import Record


def display_results(records: list[Record], fields: list[str], number: int = None) -> None:
    """Prints to display the filtered results as a list of elements with their selected fields.

    Args:
        records (list): List of results to display
        fields (list): List of fields(String) to display
              it needs to be a list of string (["field"] or ["field1", "field2"])
        number (int): the number of displayed results
               default value is None which displayed all existing results

    """

    print(' '.join(fields))
    if number is None or number >= len(records):
        for record in records:
            display_field_value(record, fields)
    else:
        print("Number of displayed results: " + str(number) + '\n')
        for record in records[:number]:
            display_field_value(record, fields)


def display_field_value(record: Record, fields: list[str]) -> None:
    """Prints the results depending on the field.

    Args:
        record (object:Record): the results to displayed
        fields(list): the fields to displayed
              it needs to be a list of string (["field"] or ["field1", "field2"])
    """
    for field in fields:
        if record.column(field).datatype == "QUANTITY":
            print(record.column(field).value, end=" ")
            print(record.column(field).unit, end=" ")
        elif record.column(field).datatype == "DATE":
            if not record.column(field).value:
                print(None, end=" ")
            elif record.column(field).subType == "date":
                print(datetime.date.fromtimestamp(record.column(field).value / 1000.0), end=" ")
            elif record.column(field).subType == "datetime":
                print(datetime.datetime.fromtimestamp(record.column(field).value / 1000.0), end=" ")
            else:
                print(time.strftime("%H:%M", time.gmtime(int(record.column(field).value) / 1000)), end=" ")
        else:
            print(record.column(field).value, end=" ")
    print(end='\n',)
