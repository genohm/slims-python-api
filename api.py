import httplib
import json
import types

from base64 import b64encode


class Slims(object):

    def __init__(self, url, webapp, port, username, password):
        self.url = url
        self.webapp = webapp
        self.port = port
        self.username = username
        self.password = password

    def _auth(self):
        user_and_pass = b64encode(self.username + ":" + self.password).decode("ascii")
        headers = {}
        headers['Authorization'] = 'Basic %s' % user_and_pass
        headers["Content-Type"] = "application/json"
        return headers

    def _createConnection(self, url, method, body={}):
        conn = httplib.HTTPConnection(self.url, self.port)
        conn.request(method, self.webapp + "/rest/" + url, json.dumps(body), headers=self._auth())
        return conn

    def fetch(self, table, criteria):
        conn = self._createConnection(table + "?" + criteria, "GET")
        response = json.loads(conn.getresponse().read())
        records = []
        for entity in response["entities"]:
            records.append(Record(entity))
        return records


class Record(object):

    def __init__(self, json_entity):

        self.columns = {}
        self.json_entity = json_entity

        for json_column in json_entity["columns"]:
            column = Column(json_column)
            self.columns[column.name()] = column

            def getColumn(self):
                return self.column(column.name())

            self.__dict__[column.name()] = types.MethodType(getColumn, self)

    def column(self, name):
        return self.columns[name]


class Column(object):

    def __init__(self, jsonColumn):
        self.values = {}
        self.values["name"] = jsonColumn["name"]
        self.values["value"] = jsonColumn["value"]

    def name(self):
        return self.values["name"]

    def value(self):
        return self.values["value"]


def test():
    slims = Slims("localhost", "", 9999, "admin", "admin")
    records = slims.fetch("Content", "cntn_barCode=00000004")
    for record in records:
        print(record.cntn_cf_fk_barcode_i5().value())

    locations = slims.fetch("Location", "lctn_barCode=00000001")
    for record in locations:
        print(record.lctn_barCode().value())

test()
