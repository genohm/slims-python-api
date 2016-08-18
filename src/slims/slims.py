import base64
import os
import logging
import requests
import sched
import time
import threading
from flask import request as flaskrequest
from flask import Flask, jsonify
from werkzeug.local import Local

from .flowrun import FlowRun

app = Flask(__name__)
slims_instances = {}
local = Local()
logger = logging.getLogger('genohm.slims.slims')
logging.basicConfig(level=logging.INFO)


def slims_local():
    return local


@app.route("/<name>/<operation>/<step>", methods=["POST"])
def start_step(name, operation, step):
    data = flaskrequest.json
    flow_information = data['flowInformation']

    logger.info("Executing " + str(flow_information['flowId']) + " step " + step)
    return_value = slims_instances[name]._execute_operation(operation, step, data)
    if return_value:
        return jsonify(**return_value)
    else:
        return jsonify(**{})


def flask_thread(port):
    app.run(port=port)


class SlimsApiException(Exception):
    pass


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
                                json=body)
        records = []
        if response.status_code == 200:
            for entity in response.json()["entities"]:
                if entity["tableName"] == "Attachment":
                    records.append(Attachment(entity, self))
                else:
                    records.append(Record(entity, self))
            return records
        else:
            raise SlimsApiException("Could not fetch entities: " + response.text)

    def get(self, url):
        return requests.get(self.url + url,
                            auth=(self.username, self.password), headers=SlimsApi._headers())

    def post(self, url, body):
        return requests.post(self.url + url, json=body,
                             auth=(self.username, self.password), headers=SlimsApi._headers())

    def put(self, url, body):
        return requests.put(self.url + url, json=body,
                            auth=(self.username, self.password), headers=SlimsApi._headers())

    def delete(self, url):
        return requests.delete(self.url + url,
                               auth=(self.username, self.password), headers=SlimsApi._headers())

    @staticmethod
    def _headers():
        try:
            return {'X-SLIMS-REQUESTED-FOR': local.user}
        except AttributeError:
            return {}


class Slims(object):

    def __init__(self,
                 name,
                 url,
                 username=None,
                 password=None,
                 token=None,
                 repo_location=None,
                 local_host="localhost",
                 local_port=5000):

        """
        Creates a new slims instance to work with

        Parameters:
        name -- The name of this slims instance
        url -- The url of the REST API of this slims instance
        username (optional) -- The username to login with (needed for standard operations)
        password (optional) -- The password to login with (needed for standard operations)
        token (optional) -- The token to login with (needed to add SLimsGate flows)
        repo_location (optional) -- The location of the file repository (this can
            be used to access attachments without needing to download them)
        local_host (optional) -- The IP on which this python script is running
            Needed for SLimsGate flows. SLims will contact the python script on this
            url. Defaults to "localhost"
        local_port (optional) -- The port on which this python script is running
            Needed for ports. SLims will contact the python script on this
            ports. Defaults to "5000"
        """
        slims_instances[name] = self
        if username is not None and password is not None:
            self.slims_api = SlimsApi(url, username, password, repo_location)
        elif token is not None:
            self.slims_api = SlimsApi(url, "TOKEN", token, repo_location)
        else:
            raise Exception("Either specify a username and a password or a token")

        self.name = name
        self.operations = {}
        self.flow_definitions = []
        self.refresh_flows_thread = threading.Thread(target=self._refresh_flows_thread_inner)
        self.refresh_flows_thread.daemon = True
        self.local_host = local_host
        self.local_port = local_port

    def fetch(self, table, criteria, sort=[], start=None, end=None):
        """Fetch data by criteria

        The optional start and end parameters can be used to page the returned
        results.

        Parameters:
        table -- The table to fetch from
        criteria -- The criteria to match
        sort (optional) -- The fields to sort on
        start (optional)--  The first row to return
        end (optional) -- The last row to return
        """
        body = {
            "sortBy": sort,
            "startRow": start,
            "endRow": end,
        }
        if criteria:
            body["criteria"] = criteria.to_dict()

        return self.slims_api.get_entities(table + "/advanced", body=body)

    def fetch_by_pk(self, table, pk):
        """ Fetch a record by primary key

        Parameters:
        table -- The table of the record
        pk -- The primary key of the record
        """
        entities = self.slims_api.get_entities(table + "/" + str(pk))
        if len(entities) > 0:
            return entities[0]
        else:
            return None

    def add(self, table, values):
        """ Add a new record

        Parameters:
        table -- Table where the element need to be added.
        values -- a dictionary with the values of the record.
        """
        response = self.slims_api.put(url=table, body=values).json()
        new_values = response["entities"][0]
        return Record(new_values, self.slims_api)

    def add_flow(self, flow_id, name, usage, steps, testing=False):
        """Allows to add a SLimsGate flow in SLims interface.

        Parameters:
        flow_id -- name of the id of the flow_id.
        name -- name of the flow that will be displayed in SLims interface.
        usage -- name indicating in which table the flow can be called.
        steps -- a list of steps elements that needs to be executed.
        """
        step_dicts = []
        i = 0
        for step in steps:
            url = flow_id + "/" + repr(i)
            step_dicts.append(step.to_dict(url))
            self.operations[url] = step
            i += 1

        flow = {'id': flow_id, 'name': name, 'usage': usage, 'steps': step_dicts, 'pythonApiFlow': True}
        self.flow_definitions.append(flow)
        self._register_flows([flow], False)

        if not testing:
            if not self.refresh_flows_thread.is_alive():
                self.refresh_flows_thread.start()
            flask_thread(self.local_port)

    def _register_flows(self, flows, is_reregister):
        flow_ids = map(lambda flow: flow.get('id'), flows)
        verb = "re-register" if is_reregister else "register"

        try:
            instance = {'url': "http://" + self.local_host + ':' + str(self.local_port), 'name': self.name}
            body = {'instance': instance, 'flows': flows}
            response = self.slims_api.post("external/", body)

            if response.status_code == 200:
                logger.info("Successfully " + verb + "ed " + str(flow_ids))
            else:
                logger.info("Could not " + verb + " " + str(flow_ids) +
                            " (HTTP Response code: " + str(response.status_code) + ")")
                try:
                    logger.info("Reason: " + response.json()["errorMessage"])
                except Exception:
                    # Probably no json was sent
                    pass
        except Exception:
            logger.info("Could not " + verb + " flows " + str(flow_ids) + " trying again in 60 seconds")

    def _execute_operation(self, operation, step, data):
        flow_run = FlowRun(self.slims_api, step, data)
        output = self.operations[operation + "/" + str(step)].execute(flow_run)
        return output

    def _refresh_flows_thread_inner(self):
        def refresh_flows(scheduler):
            self._register_flows(self.flow_definitions, True)
            scheduler.enter(60, 1, refresh_flows, (scheduler,))

        scheduler = sched.scheduler(time.time, time.sleep)
        scheduler.enter(60, 1, refresh_flows, (scheduler,))
        scheduler.run()


class Record(object):

    def __init__(self, json_entity, slims_api):
        self.json_entity = json_entity
        self.slims_api = slims_api

        for json_column in json_entity["columns"]:
            column = Column(json_column)
            self.__dict__[column.name] = column

    def update(self, values):
        """
        Updates this record with new values.

        Example:
            content = slims.fetch_by_pk("Content", 1)
            updated_content = content.update({"cntn_id": "new_id"})

        Parameters:
        values -- dictionary with new values

        returns:
        the updated record
        """
        url = self.table_name() + "/" + str(self.pk())
        response = self.slims_api.post(url=url, body=values).json()
        new_values = response["entities"][0]
        return Record(new_values, self.slims_api)

    def remove(self):
        """
        Removes this record.
        """
        url = self.table_name() + "/" + str(self.pk())
        response = self.slims_api.delete(url=url)
        if response.status_code != 200:
            raise Exception("Delete failed: " + response.text)

    def table_name(self):
        """
        Returns the name of the table of this record
        """
        return self.json_entity["tableName"]

    def pk(self):
        """
        Returns the primary key of this record
        """
        return self.json_entity["pk"]

    def attachments(self):
        """
        Returns the attachments related to this record
        """
        return self.slims_api.get_entities(
            "attachment/" + self.json_entity["tableName"] + "/" + str(self.json_entity["pk"]))

    def add_attachment(self, name, byte_array):
        """Adds an attachment to a record (over HTTP).

        Example uses:
          * content.add_attachment("test.txt", b"Hi from python")
          * with open(file_name, 'rb') as to_upload:
                content.add_attachment("test.txt", to_upload.read())

        Parameters:
        name -- The name of the attachment
        byte_array -- The binary content of the attachment
        Returns:
        The primary key of the added attachment
        """

        body = {
            "attm_name": name,
            "atln_recordPk": self.pk(),
            "atln_recordTable": self.table_name(),
            "contents": base64.b64encode(byte_array).decode("utf-8")
        }
        response = self.slims_api.post(url="repo", body=body)
        location = response.headers['Location']
        return int(location[location.rfind("/") + 1:])

    def column(self, column_name):
        """
        Returns a column of the record

        Parameters:
        column_name -- name of the column.
        """
        return self.__dict__[column_name]

    def follow(self, link_name):
        """
        Follows an incoming or outgoing foreign key

        Examples:
            - content_type = slims.fetch_by_pk("Content", 1L)
                    .follow("cntn_fk_contentType")
            This fetches the content record with primary key 1 and then fetches
            its content type (one record).

            - results = slims.fetch_by_pk("Content", 1L)
                    .follow("-rslt_fk_content")

            This fetches the content record with primary key 1 and then fetches
            its results (a list of records)


        Parameters:
        link_name -- field linking two tables.
            The links should start with a - (minus) if the link is incoming.
        """
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
        """
        Returns the location of an attachment on disk
        """
        if self.slims_api.repo_location:
            return os.path.join(self.slims_api.repo_location, self.attm_path.value)
        else:
            raise RuntimeError("no repo_location configured")

    def download_to(self, location):
        """
        Downloads an attachment to a file on disk

        Example uses:
          * attachment.download_to("test.txt")

        Parameters:
        location -- The name of the file the attachment should be downloaded to
        """
        with open(location, 'wb') as destination:
            response = self.slims_api.get("repo/" + str(self.pk()))
            destination.write(response.content)


class Column(object):

    def __init__(self, json_column):
        self.__dict__.update(json_column)
