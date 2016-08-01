import unittest
import json

import requests
import responses

from genohm.slims.slims import Slims
from genohm.slims.step import *
from genohm.slims.criteria import *


class Test_Adding_Flow(unittest.TestCase):

    @responses.activate
    def test_adding_flow(self):

        def execute_first_step(data):
            pass

        def add_flow_callback(request):
            body = json.loads(request.body)
            self.assertDictEqual(
                body,
                {'instance': {'url': 'http://localhost:5000', 'name': 'testSlims'},
                 'flow':
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
                     ]
                     }
                 })

            return (200, {}, json.dumps({}))

        responses.add_callback(
            responses.POST,
            'http://localhost:9999/rest/external/',
            callback=add_flow_callback,
            content_type='application/json',
        )

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
                        text_input("text", "Text")
                    ],
                    output=[
                        file_output()
                    ]
                )
            ],
            testing=True)
