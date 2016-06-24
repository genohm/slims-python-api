import requests
from flask import Flask

app = Flask(__name__)
slims_instances = {}


@app.route("/<name>/<operation>")
def hello(name, operation):
    slims_instances[name]._execute_operation(operation)
    return "Hello World!" + operation


def flaskThread():
    app.run()


class Slims(object):

    def __init__(self, name, url, username, password):
        slims_instances[name] = self

        self.name = name
        self.url = url + "/rest/"
        self.username = username
        self.password = password
        self.operations = {}

    def _get(self, url):
        return requests.get(self.url + url, auth=(self.username, self.password)).json()

    def _post(self, url, body):
        return requests.post(self.url + url, json=body, auth=(self.username, self.password))

    def fetch(self, table, criteria):
        response = self._get(table + "?" + criteria)
        records = []
        for entity in response["entities"]:
            records.append(Record(entity))
        return records

    def register(self, operation):
        self.operations[operation.name()] = operation
        body = {"url": "http://localhost:5000",
                "name": self.name,
                "operation": operation.name()}

        response = self._post("external/", body)

        if response.status_code == 200:
            print "Successfully registered " + operation.name()
        else:
            print "Could not register " + operation.name() + "(" + response.status_code + ")"

        flaskThread()

    def _execute_operation(self, operation):
        self.operations[operation].execute()


class Record(object):

    def __init__(self, json_entity):

        self.columns = {}
        self.json_entity = json_entity

        for json_column in json_entity["columns"]:
            column = Column(json_column)
            self.columns[column.name()] = column
#
# Currently disabled does not work yet (or ever)
#           def get_column(self):
#               return column
#           self.__dict__[column.name()] = types.MethodType(get_column, self)

    def column(self, name):
        return self.columns[name]


class Column(object):

    def __init__(self, json_column):
        self.values = {
            "name": json_column["name"],
            "value": json_column["value"]}

    def name(self):
        return self.values["name"]

    def value(self):
        return self.values["value"]
