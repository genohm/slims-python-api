from slims.slims import Slims
from slims.step import Step, text_input, single_choice_with_value_map_input

"""
This example demonstrates a very simple two step flow. In the first step
a content record can be selected in the UI. In the second step a new id
for that content record can be chosen.
"""


def do_nothing(flow_run):
    print("Do nothing")


def execute(flow_run):
    content_to_modify = slims.fetch_by_pk("Content",
                                          flow_run.data["content_to_modify"])
    content_to_modify.update({"cntn_id": flow_run.data["id"]})


slims = Slims("slims", "http://localhost:9999", token="devToken")

slims.add_flow(
    flow_id="updateContentId",
    name="Update content id",
    usage="CONTENT_MANAGEMENT",
    steps=[
        Step(
            name="Select content to update",
            action=do_nothing,
            input=[
                single_choice_with_value_map_input(
                    "content_to_modify",
                    "Content to modify",
                    "Content",
                    # Persistent will make sure the parameter is also passed
                    # into all the next steps
                    persistent=True)
            ]
        ),
        Step(
            name="Fill in id",
            action=execute,
            input=[
                text_input("id", "New ID")
            ]
        )
    ])
