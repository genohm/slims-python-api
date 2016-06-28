from flask import Flask
from flask import jsonify
from flask import request as flaskrequest
from flowrun import FlowRun

import base64
import requests
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
slims_instances = {}


@app.route("/<name>/<operation>/<step>", methods=["POST"])
def hello(name, operation, step):
    data = flaskrequest.json
    returnValue = slims_instances[name]._execute_operation(operation, step, data)
    return jsonify(**returnValue)


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

    def add_flow(self, flow_id, name, usage, steps):
        step_dicts = []
        i = 0
        for step in steps:
            url = flow_id + "/" + repr(i)
            step_dicts.append(step.to_dict(url))
            self.operations[url] = step.action
            i += 1

        flow = {'id': flow_id, 'name': name, 'usage': usage, 'steps': step_dicts}
        instance = {'url': 'http://localhost:5000', 'name': self.name}
        body = {'instance': instance, 'flow': flow}
        response = self._post("external/", body)

        if response.status_code == 200:
            print "Successfully registered " + flow_id
        else:
            print "Could not register " + flow_id + "(" + str(response.status_code) + ")"

        flaskThread()

    def _execute_operation(self, operation, step, data):
        flowrun = FlowRun(self, step, data)
        output = self.operations[operation + "/" + str(step)](flowrun)
        if type(output) is file:
            return {'bytes': base64.b64encode(output.read()), 'fileName': output.name}
        else:
            return output


class Record(object):

    def __init__(self, json_entity):
        self.json_entity = json_entity

        for json_column in json_entity["columns"]:
            column = Column(json_column)
            self.__dict__[column.name] = column

    def column(self, name):
        return self.__dict__[name]


class Column(object):

    def __init__(self, json_column):
        self.__dict__.update(json_column)
