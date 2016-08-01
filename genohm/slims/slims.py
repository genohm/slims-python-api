from flask import Flask
from flask import jsonify
from flask import request as flaskrequest
from .flowrun import FlowRun
from werkzeug.local import Local
import os

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

    def __init__(self, url, username, password, repo_location):
        self.url = url + "/rest/"
        self.username = username
        self.password = password
        self.repo_location = repo_location

    def get_entities(self, url, body=None):
        if not url.startswith(self.url):
            url = self.url + url

        response = requests.get(url,
                                auth=(self.username, self.password),
                                headers=SlimsApi._headers(),
                                json=body).json()
        records = []
        for entity in response["entities"]:
            if entity["tableName"] == "Attachment":
                records.append(Attachment(entity, self))
            else:
                records.append(Record(entity, self))

        return records

    def post(self, url, body):
        return requests.post(self.url + url, json=body,
                             auth=(self.username, self.password), headers=SlimsApi._headers())

    def put(self, url, body):
        return requests.put(self.url + url, json=body,
                            auth=(self.username, self.password), headers=SlimsApi._headers())

    @staticmethod
    def _headers():
        try:
            return {'X-SLIMS-REQUESTED-FOR': local.user}
        except AttributeError:
            return {}


class Slims(object):

    def __init__(self, name, url, username, password, repo_location=None):
        slims_instances[name] = self
        self.slims_api = SlimsApi(url, username, password, repo_location)
        self.name = name
        self.operations = {}

    def fetch(self, table, criteria, sort=[], start=None, end=None):
        """Allows to fetch data that match criterion

        Parameters:
        self -- instance parameter
        table -- name of the table in which the fetch takes place
        criteria -- criteria to fetch
                    it calls criteria functions
                    criterion can be added using one junction function followed
                    by add(criteria) function
        sort -- list of the fields used to sort
        start --  number representing the position in a list of the first result to display
        end  --  number representing the position in a list of the last result to display
        """
        body = {
            "criteria": criteria.to_dict(),
            "sortBy": sort,
            "startRow": start,
            "endRow": end,
        }
        return self.slims_api.get_entities(table + "/advanced", body=body)

    def fetch_by_pk(self, table, pk):
        entities = self.slims_api.get_entities(table + "/" + str(pk))
        if len(entities) > 0:
            return entities[0]
        else:
            return None

    def add(self, table, values):
        response = self.slims_api.put(url=table, body=values).json()
        new_values = response["entities"][0]
        return Record(new_values, self.slims_api)

    def add_flow(self, flow_id, name, usage, steps, testing=False):
        """Allows to add a SLimsGate flow in SLims interface.

        Parameters:
        self -- instance parameter
        flow_id -- name of the id of the flow_id
        name -- name of the flow that will be displayed in SLims interface
        usage -- name indicating in which table the flow can be called
        steps -- a list of steps elements that needs to be executed
        """
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

        if not testing:
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

    def update(self, values):
        url = self.json_entity["tableName"] + "/" + str(self.json_entity["pk"])
        response = self.slims_api.post(url=url, body=values).json()
        new_values = response["entities"][0]
        return Record(new_values, self.slims_api)

    def attachments(self):
        return self.slims_api.get_entities(
            "attachment/" + self.json_entity["tableName"] + "/" + str(self.json_entity["pk"]))

    def follow(self, link_name):
        for link in self.json_entity["links"]:
            if link["rel"] == link_name:
                href = link["href"]
                entities = self.slims_api.get_entities(href)
                if link_name.startswith("-"):
                    return entities
                else:
                    if len(entities) > 0:
                        return entities[0]
                    else:
                        return None
        raise KeyError(str(link_name) + "not found in the list of links")


class Attachment(Record):

    def __init__(self, json_entity, slims_api):
        super(Attachment, self).__init__(json_entity, slims_api)

    def get_local_path(self):
        if self.slims_api.repo_location:
            return os.path.join(self.slims_api.repo_location, self.attm_path.value)
        else:
            raise RuntimeError("no repo_location configured")


class Column(object):

    def __init__(self, json_column):
        self.__dict__.update(json_column)
