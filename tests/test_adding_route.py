from genohm.slims import Slims
from genohm.step import *


def execute_first_step(data):
    print "Hello " + str(data['name'])
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
