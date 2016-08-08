from slims.slims import Slims
from slims.step import text_input
from slims.step import Step
from slims.criteria import equals


def execute_first_step(flow_run):
    print(slims.fetch("Content", equals("cntn_id", "b")))

slims = Slims("testSlims", "http://localhost:9999", token="abc")

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
        )
    ])
