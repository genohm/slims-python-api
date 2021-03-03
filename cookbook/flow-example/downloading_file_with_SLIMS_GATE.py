from slims.output import file_value
from slims.slims import Slims
from slims.step import Step, file_output


def execute():
    # Make sure the path to the file exists
    return file_value('C:/Users/User/Downloads/file.txt')


slims = Slims("slims", url="http://127.0.0.1:9999/", token="devToken", local_host="0.0.0.0", local_port=5000)


slims.add_flow(
    flow_id="FLOW_0001",
    name="Download an file from server",
    usage="CONTENT_MANAGEMENT",
    steps=[
        Step(
            name="This downloads a file.",
            action=execute,
            output=[
                file_output()
            ])
    ])
