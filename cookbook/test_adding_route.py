from genohm.slims.slims import Slims
from genohm.slims.step import *
from genohm.slims.output import file_value
import time


def execute_first_step(flow_run):
    for i in range(1, 20):
        time.sleep(1)
        flow_run.log("Hallo " + str(i))
    return file_value("/Users/ruben/git/slims-python-api/dependencies.txt")

print text_input("name", "label")

slims = Slims("testSlims", "http://localhost:9999", "admin", "admin")

slims.add_flow(
    flow_id="myFlow",
    name="My flow in python",
    usage="CONTENT_MANAGEMENT",
    steps=[
        Step(
            name="first step",
            action=execute_first_step,
            input=[
                # multiple_choice_with_value_map_input("name", "label", "Content")
                # single_choice_with_value_map_input("name", "label", "Content")
                # rich_text_input("Text", "Text")
                # boolean_input("Boolean", "Boolean")
                # time_input("Time", "time")
                date_input("Date", "Date")
                # date_time_input("DateTime", "DateTime")
                # multiple_choice_with_field_list_input("Location", "select location",
                #                                        ["Hi", "Good Morning", "Hello"], [None, None, None])
                # text_input("name", "label", defaultValue= "a default value")
                # default_value(integer_input("name1", "label1"), "19")
                # table_input("name", "label", [text_input("name", "label"), boolean_input("boolean", "boolean")])
            ],
            output=[
                file_output()
            ]
        )
    ])
