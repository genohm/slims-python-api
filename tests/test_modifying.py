import unittest

import pytest
import responses

from slims.internal import Record, _SlimsApiException

from slims.slims import Slims


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
        assert isinstance(updated, Record)

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
        assert isinstance(added, Record)

    @responses.activate
    def test_remove_success(self):
        responses.add(
            responses.DELETE,
            'http://localhost:9999/rest/Content/1',
            content_type='application/json',
        )

        slims = Slims("testSlims", "http://localhost:9999", "admin", "admin")
        record = Record({"pk": 1,
                         "tableName": "Content",
                         "columns": []},
                        slims.slims_api)

        record.remove()

    @responses.activate
    def test_remove_failure(self):
        responses.add(
            responses.DELETE,
            'http://localhost:9999/rest/Content/1',
            content_type='application/json',
            body="Could not delete",
            status=400
        )

        slims = Slims("testSlims", "http://localhost:9999", "admin", "admin")
        record = Record({"pk": 1,
                         "tableName": "Content",
                         "columns": []},
                        slims.slims_api)

        pytest.raises(_SlimsApiException, record.remove)
