from genohm.slims import Slims
from genohm.step import *
import time


def execute_first_step(flowRun):
    print(flowRun.data)
    for i in range(1, 10):
        time.sleep(1)
        print(str(i))
        flowRun.log("Hello message " + str(i))

    print "Hello " + str(flowRun.data['name'])
    return open('/Users/Ruben/git/slims-python-api/.gitignore', 'r')


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
