from genohm.slims import Slims
from genohm.step import *
import time


def execute_first_step(flow_run):
    records = slims.fetch("Content", "cntn_barCode=00000004")

    flow_run.log("Hallo")
    time.sleep(10)
    for record in records:
        print(str(record.update({"cntn_cf_custombarcode": flow_run.data["name"]})))

    return open('/Users/Ruben/git/slims-python-api/.gitignore', 'r')


slims = Slims("testSlims", "http://localhost:9999", "ruben", "ruben")

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
