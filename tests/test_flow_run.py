import unittest
import json
import responses

from slims.slims import Slims
from slims.flowrun import FlowRun
from slims.flowrun import Status


class Test_Flow_Run(unittest.TestCase):

    @responses.activate
    def test_logging(self):
        def request_callback(request):
            body = json.loads(request.body.decode('utf-8'))
            self.assertDictEqual({'flowRunGuid': 'guid', 'index': 0, 'message': 'hi'}, body)
            return (200, {}, json.dumps({}))

        responses.add_callback(
            responses.POST,
            'http://localhost:9999/rest/external/log',
            callback=request_callback,
            content_type='application/json',
        )

        slims = Slims("testSlims", "http://localhost:9999", "admin", "admin")
        flowrun = FlowRun(slims.slims_api, 0, {
            "flowInformation": {"flowRunGuid": "guid"}
        })
        flowrun.log("hi")

    @responses.activate
    def test_update_status(self):
        def request_callback(request):
            body = json.loads(request.body.decode('utf-8'))
            self.assertDictEqual({'flowRunGuid': 'guid', 'index': 0, 'status': 'FAILED'}, body)
            return (200, {}, json.dumps({}))

        responses.add_callback(
            responses.POST,
            'http://localhost:9999/rest/external/status',
            callback=request_callback,
            content_type='application/json',
        )

        slims = Slims("testSlims", "http://localhost:9999", "admin", "admin")
        flowrun = FlowRun(slims.slims_api, 0, {
            "flowInformation": {"flowRunGuid": "guid"}
        })
        flowrun._update_status(Status.FAILED)
