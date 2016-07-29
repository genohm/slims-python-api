import unittest
import json

import requests
import responses

from genohm.slims.slims import Slims
from genohm.slims.criteria import *


class Test_Fetching_Data(unittest.TestCase):

    @responses.activate
    def test_fetch_by_pk(self):
        responses.add(
            responses.GET,
            'http://localhost:9999/rest/Content/1',
            json={"entities": [{
                "pk": 1,
                "tableName": "Content",
                "columns": [
                    {
                        "datatype": "STRING",
                        "name": "cntn_id",
                        "title": "Id",
                        "position": 2,
                        "value": "sample1",
                        "hidden": False,
                        "editable": False
                    },
                ]}]},
            content_type='application/json',
        )

        slims = Slims("testSlims", "http://localhost:9999", "admin", "admin")
        entity = slims.fetch_by_pk("Content", 1)
        self.assertEqual(entity.cntn_id.value, "sample1")

    @responses.activate
    def test_fetch_advanced(self):

        def request_callback(request):
            body = json.loads(request.body)
            self.assertEqual(body["startRow"], 0)
            self.assertEqual(body["endRow"], 1)
            self.assertEqual(body["sortBy"], ["cntn_createdOn"])
            self.assertEqual(body["criteria"]["operator"], "equals")
            self.assertEqual(body["criteria"]["fieldName"], "cntn_id")
            self.assertEqual(body["criteria"]["value"], "test")

            return (200, {}, json.dumps({"entities": []}))

        responses.add_callback(
            responses.GET,
            'http://localhost:9999/rest/Content/advanced',
            callback=request_callback,
            content_type='application/json',
        )

        slims = Slims("testSlims", "http://localhost:9999", "admin", "admin")
        entities = slims.fetch("Content",
                               equals("cntn_id", "test"),
                               sort=["cntn_createdOn"],
                               start=0,
                               end=1)
