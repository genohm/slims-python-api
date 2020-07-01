import unittest
import json
import responses

from slims.slims import Slims
from slims.slims import Record
from slims.slims import Attachment
from slims.criteria import equals


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
    def test_fetch_by_pk_nothing_returned(self):
        responses.add(
            responses.GET,
            'http://localhost:9999/rest/Content/1',
            json={"entities": []},
            content_type='application/json',
        )

        slims = Slims("testSlims", "http://localhost:9999", "admin", "admin")
        entity = slims.fetch_by_pk("Content", 1)
        self.assertEqual(entity, None)

    @responses.activate
    def test_fetch_advanced(self):

        def request_callback(request):
            body = json.loads(request.body.decode('utf-8'))
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
        self.assertEquals(entities, [])

    @responses.activate
    def test_fetch_incoming_link(self):
        responses.add(
            responses.GET,
            'http://localhost:9999/rest/Content/1',
            json={"entities": [{
                "pk": 1,
                "tableName": "Content",
                "columns": [],
                "links": [
                    {
                        "rel": "cntn_fk_contentType",
                        "href": "http://localhost:9999/rest/ContentType/2"
                    },
                    {
                        "rel": "cntn_fk_location",
                        "href": "http://localhost:9999/rest/Location/3"
                    },
                ]}]},
            content_type='application/json',
        )

        responses.add(
            responses.GET,
            'http://localhost:9999/rest/ContentType/2',
            json={"entities": [{
                "pk": 2,
                "tableName": "ContentType",
                "columns": []}]},
            content_type='application/json',
        )

        responses.add(
            responses.GET,
            'http://localhost:9999/rest/Location/3',
            json={"entities": []},
            content_type='application/json',
        )

        slims = Slims("testSlims", "http://localhost:9999", "admin", "admin")
        entity = slims.fetch_by_pk("Content", 1)
        self.assertIsInstance(entity.follow("cntn_fk_contentType"), Record)
        self.assertEqual(entity.follow("cntn_fk_location"), None)

    @responses.activate
    def test_fetch_outgoing_link(self):
        responses.add(
            responses.GET,
            'http://localhost:9999/rest/Content/1',
            json={"entities": [{
                "pk": 1,
                "tableName": "Content",
                "columns": [],
                "links": [
                    {
                        "rel": "-rslt_fk_content",
                        "href": "http://localhost:9999/rest/Result?rslt_fk_content=1"
                    },
                ]}]},
            content_type='application/json',
        )

        responses.add(
            responses.GET,
            # responses library filters out GET parameters
            'http://localhost:9999/rest/Result',
            json={"entities": [{
                "pk": 2,
                "tableName": "Result",
                "columns": []}]},
            content_type='application/json',
        )

        slims = Slims("testSlims", "http://localhost:9999", "admin", "admin")
        entity = slims.fetch_by_pk("Content", 1)
        self.assertIsInstance(entity.follow("-rslt_fk_content")[0], Record)

    @responses.activate
    def test_fetch_unknown_link(self):
        responses.add(
            responses.GET,
            'http://localhost:9999/rest/Content/1',
            json={"entities": [{
                "pk": 1,
                "tableName": "Content",
                "columns": [],
                "links": []}]},
            content_type='application/json',
        )

        slims = Slims("testSlims", "http://localhost:9999", "admin", "admin")
        entity = slims.fetch_by_pk("Content", 1)
        self.assertRaises(KeyError, entity.follow, "unknown")

    @responses.activate
    def test_fetch_attachments(self):
        responses.add(
            responses.GET,
            'http://localhost:9999/rest/attachment/Content/1',
            json={"entities": [{
                "pk": 1,
                "tableName": "Attachment",
                "columns": []}]},
            content_type='application/json',
        )
        slims = Slims("testSlims", "http://localhost:9999", "admin", "admin")
        record = Record({"pk": 1,
                         "tableName": "Content",
                         "columns": []},
                        slims.slims_api)

        attachments = record.attachments()
        self.assertIsInstance(attachments[0], Attachment)
