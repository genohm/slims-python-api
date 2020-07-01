import unittest
import responses
import json
import tempfile
import os

from slims.slims import Slims
from slims.slims import Attachment
from slims.slims import Record


class Test_Attachments(unittest.TestCase):

    attachmentValues = {"pk": 1,
                        "tableName": "Attachment",
                        "columns": [{
                            "name": "attm_path",
                            "value": "a/file.txt"
                        }]}

    contentValues = {"pk": 1,
                     "tableName": "Content",
                     "columns": []}

    def test_attachment_path_without_repo_location_throws(self):
        slims = Slims("testSlims", "http://localhost:9999", "admin", "admin")
        attachment = Attachment(self.attachmentValues, slims.slims_api)
        self.assertRaises(RuntimeError, attachment.get_local_path)

    def test_attachment_path_with_repo_location(self):
        slims = Slims("testSlims", "http://localhost:9999", "admin", "admin", repo_location="/var/slims/repo")
        attachment = Attachment(self.attachmentValues, slims.slims_api)
        self.assertEqual("/var/slims/repo" + os.sep + "a/file.txt", attachment.get_local_path())

    @responses.activate
    def test_add_attachment(self):

        def add_attachment_callback(request):
            body = json.loads(request.body.decode('utf-8'))
            self.assertDictEqual(
                body,
                {"atln_recordPk": 1,
                 "atln_recordTable": "Content",
                 "attm_name": "test.txt",
                 "contents": 'U29tZSB0ZXh0'})

            return (200, {"Location": "http://localhost:9999/rest/Attachment/2"}, json.dumps({}))

        responses.add_callback(
            responses.POST,
            'http://localhost:9999/rest/repo',
            callback=add_attachment_callback,
            content_type='application/json',
        )

        slims = Slims("testSlims", "http://localhost:9999", "admin", "admin", repo_location="/var/slims/repo")
        content = Record(self.contentValues, slims.slims_api)
        self.assertEqual(2, content.add_attachment("test.txt", b"Some text"))

    @responses.activate
    def test_download_attachment(self):

        def repo_request_callback(request):
            return (200, {}, "blabla")

        responses.add_callback(
            responses.GET,
            'http://localhost:9999/rest/repo/1',
            callback=repo_request_callback,
            content_type='application/json',
        )

        slims = Slims("testSlims", "http://localhost:9999", "admin", "admin", repo_location="/var/slims/repo")
        attachment = Attachment(self.attachmentValues, slims.slims_api)
        temp = tempfile.NamedTemporaryFile(delete=False)
        filename = temp.name
        temp.close()
        attachment.download_to(filename)
        with open(filename, 'r') as file:
            self.assertEqual("blabla", file.read())
        os.remove(temp.name)
