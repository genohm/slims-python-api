from slims.slims import Slims
from slims.step import Step, integer_input, text_input


def execute_first_step(flow_run):
    print("Do nothing")

slims = Slims("testSlims", "http://localhost:9999", token="devToken")

slims.add_flow(
    flow_id="myFlow",
    name="My flow in python",
    usage="CONTENT_MANAGEMENT",
    steps=[
        Step(
            name="first step",
            action=execute_first_step,
            input=[
                text_input("Date", "Date")
            ]
        ),
        Step(
            name="2d step",
            action=execute_first_step,
            input=[
                integer_input("Patients", "Patients", defaultValue="0")
            ]
        ),
        Step(
            name="3d step",
            action=execute_first_step,
            input=[
                integer_input("Test", "Test", defaultValue="0")
            ]
        )
    ])
