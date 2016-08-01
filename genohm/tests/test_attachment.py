import unittest

from genohm.slims.slims import Slims
from genohm.slims.slims import Attachment


class Test_Attachments(unittest.TestCase):

    attachmentValues = {"pk": 1,
                        "tableName": "Content",
                        "columns": [{
                            "name": "attm_path",
                            "value": "a/file.txt"
                        }]}

    def test_attachment_path_without_repo_location_throws(self):
        slims = Slims("testSlims", "http://localhost:9999", "admin", "admin")
        attachment = Attachment(self.attachmentValues, slims.slims_api)
        self.assertRaises(RuntimeError, attachment.get_local_path)

    def test_attachment_path_with_repo_location(self):
        slims = Slims("testSlims", "http://localhost:9999", "admin", "admin", repo_location="/var/slims/repo")
        attachment = Attachment(self.attachmentValues, slims.slims_api)
        self.assertEqual("/var/slims/repo/a/file.txt", attachment.get_local_path())
