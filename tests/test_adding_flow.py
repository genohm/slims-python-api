import json
import unittest

import responses

from slims.slims import Slims
from slims.step import Step, file_output, text_input


class Test_Adding_Flow(unittest.TestCase):

    @responses.activate
    def test_adding_flow(self):
        def execute_first_step(data):
            pass

        rsp = responses.post(
            'https://localhost:9999/rest/external/',
            status=200,
            content_type='application/json',
        )

        slims = Slims("testSlims", "https://localhost:9999", oauth=True, client_id="client_id", client_secret="secret")
        slims.add_flow(
            flow_id="myFlow",
            name="My flow in python",
            usage="CONTENT_MANAGEMENT",
            steps=[
                Step(
                    name="first step",
                    action=execute_first_step,
                    input=[
                        text_input("text", "Text")
                    ],
                    output=[
                        file_output()
                    ]
                )
            ],
            testing=True)

        assert rsp.call_count == 1
        body = json.loads(rsp.calls[0].request.body.decode('utf-8'))
        assert body == {
            'instance': {'url': 'http://localhost:5000', 'name': 'testSlims'},
            'flows': [
                {'id': 'myFlow',
                 'name': 'My flow in python',
                 'usage': 'CONTENT_MANAGEMENT',
                 'steps': [
                     {'hidden': False,
                      'name': 'first step',
                      'input': {'parameters': [{'type': 'STRING', 'name': 'text', 'label': 'Text'}]},
                      'process': {'route': 'myFlow/0', 'asynchronous': False},
                      'output': {'parameters': [{'type': 'FILE', 'name': 'file'}]}
                      }
                 ],
                 'pythonApiFlow': True}]
        }
