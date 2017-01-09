from slims.slims import Slims
from slims.step import Step, text_input, single_choice_with_value_map_input

"""
This example demonstrates a very simple two steps flow. In the first step
a content record can be selected in the UI. In the second step a new id
for that content record can be chosen.

In Slims following parameters in lab settings should be configured:
- Slims python-api token = devToken
- Slims Python-api allowd urls and flow-ids = http://127.0.0.1:5000->updateContentId
run this script using the underneath command in the folder containing it.
python id_modification.py

then open slims instance and start the flow as a SlimsGate flow from the content
module
"""


def do_nothing(flow_run):
    print("Do nothing")


def execute(flow_run):
    content_to_modify = slims.fetch_by_pk("Content",
                                          flow_run.data["content_to_modify"])
    content_to_modify.update({"cntn_id": flow_run.data["id"]})


slims = Slims("slims", "http://127.0.0.1:9999/", token="devToken")
# devToken is a parameter to be set in Slims lab Settings (Slims python-api token).
# It enables the authentication of the launcher of the flow.
# Whenever SLims is not run on the same server as python, local_host="yourIp"
# parameter in Slims() method should be set.

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
