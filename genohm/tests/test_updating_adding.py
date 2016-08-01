import unittest
import json

import requests
import responses

from genohm.slims.slims import Slims
from genohm.slims.slims import Record
from genohm.slims.criteria import *


class Test_Modifying(unittest.TestCase):

    @responses.activate
    def test_update(self):
        responses.add(
            responses.POST,
            'http://localhost:9999/rest/Content/1',
            json={"entities": [{
                "pk": 1,
                "tableName": "Content",
                "columns": []
            }]},
            content_type='application/json',
        )

        slims = Slims("testSlims", "http://localhost:9999", "admin", "admin")
        record = Record({"pk": 1,
                         "tableName": "Content",
                         "columns": []},
                        slims.slims_api)

        updated = record.update({"test": "foo"})
        self.assertIsInstance(updated, Record)

    @responses.activate
    def test_add(self):
        slims = Slims("testSlims", "http://localhost:9999", "admin", "admin")
        responses.add(
            responses.PUT,
            'http://localhost:9999/rest/Content',
            json={"entities": [{
                "pk": 1,
                "tableName": "Content",
                "columns": []
            }]},
            content_type='application/json',
        )

        added = slims.add("Content", {"test": "foo"})
        self.assertIsInstance(added, Record)
