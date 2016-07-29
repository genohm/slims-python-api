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
                text_input("name", "label")
            ],
            output=[
                file_output()
            ]
        )
    ])
