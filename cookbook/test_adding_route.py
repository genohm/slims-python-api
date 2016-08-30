from slims.slims import Slims
from slims.step import Step, integer_input, text_input
from slims.criteria import equals


def execute_first_step(flow_run):
    print(slims.fetch("Content", equals("cntn_id", "sample1")))

slims = Slims("testSlims", "http://localhost:9999", token="ruben")

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
            ],
            async=True
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
