from flask import Flask
from flask import jsonify
from flask import request as flaskrequest
from .flowrun import FlowRun
from werkzeug.local import Local

import requests

app = Flask(__name__)
slims_instances = {}
local = Local()


@app.route("/<name>/<operation>/<step>", methods=["POST"])
def hello(name, operation, step):
    data = flaskrequest.json
    local.user = data["SLIMS_CURRENT_USER"]
    return_value = slims_instances[name]._execute_operation(operation, step, data)
    if return_value:
        return jsonify(**return_value)
    else:
        return jsonify(**{})


def flask_thread():
    app.run()


class SlimsApi(object):

    def __init__(self, url, username, password):
        self.url = url + "/rest/"
        self.username = username
        self.password = password

    def get(self, url):
        return requests.get(self.url + url,
                            auth=(self.username, self.password), headers=SlimsApi._headers()).json()

    def post(self, url, body):
        return requests.post(self.url + url, json=body,
                             auth=(self.username, self.password), headers=SlimsApi._headers())

    @staticmethod
    def _headers():
        try:
            return {'X-SLIMS-REQUESTED-FOR': local.user}
        except AttributeError:
            return {}


class Slims(object):

    def __init__(self, name, url, username, password):
        slims_instances[name] = self
        self.slims_api = SlimsApi(url, username, password)
        self.name = name
        self.operations = {}

    def fetch(self, table, criteria):
        response = self.slims_api.get(table + "?" + criteria)
        records = []
        for entity in response["entities"]:
            records.append(Record(entity, self.slims_api))
        return records

    def add_flow(self, flow_id, name, usage, steps):
        step_dicts = []
        i = 0
        for step in steps:
            url = flow_id + "/" + repr(i)
            step_dicts.append(step.to_dict(url))
            self.operations[url] = step
            i += 1

        flow = {'id': flow_id, 'name': name, 'usage': usage, 'steps': step_dicts}
        instance = {'url': 'http://localhost:5000', 'name': self.name}
        body = {'instance': instance, 'flow': flow}
        response = self.slims_api.post("external/", body)

        if response.status_code == 200:
            print("Successfully registered " + flow_id)
        else:
            print("Could not register " + flow_id + "(" + str(response.status_code) + ")")

        flask_thread()

    def _execute_operation(self, operation, step, data):
        flow_run = FlowRun(self.slims_api, step, data)
        output = self.operations[operation + "/" + str(step)].execute(flow_run)
        return output


class Record(object):

    def __init__(self, json_entity, slims_api):
        self.json_entity = json_entity
        self.slims_api = slims_api

        for json_column in json_entity["columns"]:
            column = Column(json_column)
            self.__dict__[column.name] = column

    def column(self, name):
        return self.__dict__[name]

    def update(self, values):
        url = self.json_entity["tableName"] + "/" + str(self.json_entity["pk"])
        response = self.slims_api.post(url=url, body=values).json()
        new_values = response["entities"][0]
        return Record(new_values, self.slims_api)


class Column(object):

    def __init__(self, json_column):
        self.__dict__.update(json_column)
