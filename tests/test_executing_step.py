import unittest

from mock import MagicMock

from slims.step import text_input
from slims.step import file_output
from slims.step import Step
from slims.step import StepExecutionException
from slims.flowrun import Status
from slims.flowrun import FlowRun


class Test_Executing_Step(unittest.TestCase):

    def test_success(self):
        def execute_first_step(flow_run):
            print("Do Nothing")

        step = Step(name="first step",
                    action=execute_first_step,
                    input=[
                        text_input("text", "Text")
                    ],
                    output=[
                        file_output()
                    ])

        flow_run = FlowRun(None, None, None)
        flow_run.update_status = MagicMock()
        flow_run.log = MagicMock()

        step.execute(flow_run)

        flow_run.update_status.assert_called_with(Status.DONE)

    def test_fail(self):
        def execute_first_step(flow_run):
            raise Exception("went wrong")

        step = Step(name="first step",
                    action=execute_first_step,
                    input=[
                        text_input("text", "Text")
                    ],
                    output=[
                        file_output()
                    ])

        flow_run = FlowRun(None, None, None)
        flow_run.update_status = MagicMock()
        flow_run.log = MagicMock()

        self.assertRaises(StepExecutionException, step.execute, flow_run)

        flow_run.update_status.assert_called_with(Status.FAILED)
