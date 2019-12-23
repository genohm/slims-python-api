import base64
import logging
import os
import sched
import threading
import time

import requests
from flask import Flask, jsonify
from flask import request as flaskrequest
from requests_oauthlib import OAuth2Session
from werkzeug.local import Local

from .flowrun import FlowRun

app = Flask(__name__)
slims_instances = {}
local = Local()
logger = logging.getLogger('genohm.slims.slims')
logging.basicConfig(level=logging.INFO)


def _slims_local():
    return local


@app.route("/<name>/<operation>/<step>", methods=["POST"])
def _start_step(name, operation, step):
    data = flaskrequest.json
    flow_information = data['flowInformation']

    logger.info("Executing " + str(flow_information['flowId']) + " step " + step)
    return_value = slims_instances[name]._execute_operation(
        operation, step, data)
    if return_value:
        if isinstance(return_value, list):
            # FIXME hack: jsonify(**varArgs) does not work for a list
            return jsonify(return_value)
        else:
            return jsonify(**return_value)
    else:
        return jsonify(**{})


@app.route("/<instance>/token", methods=["GET"])
def _token_validator(instance):
    slims_instances[instance]._handle_oauth_code(flaskrequest.args.get('code'))
    return 'Python instance "' + instance + '" registered'


def _flask_thread(port):
    app.run(port=port, host='0.0.0.0')


class _SlimsApiException(Exception):
    pass


class _SlimsApi(object):

    def __init__(self,
                 url,
                 username,
                 password,
                 repo_location,
                 oauth=False,
                 token_updater=None,
                 redirect_url="",
                 client_id=None,
                 client_secret=None):
        self.url = url + "/rest/"
        self.raw_url = url + "/"
        self.username = username
        self.password = password
        self.repo_location = repo_location
        self.oauth = oauth
        self.client_id = client_id
        self.client_secret = client_secret
        if oauth:
            if self.client_id is None:
                raise _SlimsApiException(
                    "client_id is required when using OAuth")
            if self.client_secret is None:
                raise _SlimsApiException(
                    "client_secret is required when using OAuth")
            self.oauth_session = OAuth2Session(client_id,
                                               redirect_uri=redirect_url,
                                               scope=["api"],
                                               auto_refresh_url=self.raw_url + "oauth/token",
                                               token_updater=token_updater)

    def get_entities(self, url, body=None):
        if not url.startswith(self.url):
            url = self.url + url

        if self.oauth:
            response = self.oauth_session.get(
                url, headers=_SlimsApi._headers(), json=body)
        else:
            response = requests.get(url,
                                    auth=(self.username, self.password),
                                    headers=_SlimsApi._headers(),
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
            raise _SlimsApiException(
                "Could not fetch entities: " + response.text)

    def get(self, url):
        if self.oauth:
            return self.oauth_session.get(self.url + url,
                                          headers=_SlimsApi._headers(),
                                          client_id=self.client_id,
                                          client_secret=self.client_secret)
        else:
            return requests.get(self.url + url,
                                auth=(self.username, self.password), headers=_SlimsApi._headers())

    def post(self, url, body):
        if self.oauth:
            return self.oauth_session.post(self.url + url,
                                           json=body,
                                           headers=_SlimsApi._headers(),
                                           client_id=self.client_id,
                                           client_secret=self.client_secret)
        else:
            return requests.post(self.url + url, json=body,
                                 auth=(self.username, self.password), headers=_SlimsApi._headers())

    def put(self, url, body):
        if self.oauth:
            return self.oauth_session.put(self.url + url,
                                          json=body,
                                          headers=_SlimsApi._headers(),
                                          client_id=self.client_id,
                                          client_secret=self.client_secret)
        else:
            return requests.put(self.url + url, json=body,
                                auth=(self.username, self.password), headers=_SlimsApi._headers())

    def delete(self, url):
        if self.oauth:
            return self.oauth_session.delete(self.url + url,
                                             headers=_SlimsApi._headers(),
                                             client_id=self.client_id,
                                             client_secret=self.client_secret)
        else:
            return requests.delete(self.url + url,
                                   auth=(self.username, self.password), headers=_SlimsApi._headers())

    def authorization_url(self):
        return self.oauth_session.authorization_url(self.raw_url + "oauth/authorize")[0]

    def fetch_token(self, code):
        return self.oauth_session.fetch_token(self.raw_url + 'oauth/token',
                                              client_id=self.client_id,
                                              client_secret=self.client_secret,
                                              code=code)

    @staticmethod
    def _headers():
        try:
            return {'X-SLIMS-REQUESTED-FOR': local.user}
        except AttributeError:
            return {}


class Slims(object):
    """
    Creates a new slims instance to work with

    Args:
        name (str): The name of this slims instance
        url (str): The url of the REST API of this slims instance
        username (str, optional): The username to login with (needed for standard operations)
        password (str, optional): The password to login with (needed for standard operations)
        oauth (bool, optional): Whether Oauth authentication is used
        client_id (str, optional): The client ID used to authenticate when OAuth is true
        client_secret (str, optional): The client secret used to authenticate when OAuth is true
        repo_location (str, optional): The location of the file repository (this can
            be used to access attachments without needing to download them)
        local_host (str, optional): The IP on which this python script is running
            Needed for SLimsGate flows. SLims will contact the python script on this
            url. Defaults to "localhost"
        local_port (int, optional): The port on which this python script is running
            Needed for ports. SLims will contact the python script on this
            ports. Defaults to "5000"
    """

    def __init__(self,
                 name,
                 url,
                 username=None,
                 password=None,
                 oauth=False,
                 client_id=None,
                 client_secret=None,
                 repo_location=None,
                 local_host="localhost",
                 local_port=5000):

        slims_instances[name] = self
        self.local_host = local_host
        self.local_port = local_port
        self.local_url = "http://" + self.local_host + \
            ":" + str(self.local_port) + "/"
        if username is not None and password is not None:
            self.slims_api = _SlimsApi(url, username, password, repo_location)
        elif oauth:
            self.slims_api = _SlimsApi(url,
                                       "OAUTH",
                                       "oauth",
                                       repo_location,
                                       True,
                                       self.token_updater,
                                       self.local_url + name + "/token",
                                       client_id=client_id,
                                       client_secret=client_secret)
            self.token = None
        else:
            raise Exception(
                "Either specify a username and a password or use oauth")

        self.name = name
        self.oauth = oauth
        self.operations = {}
        self.flow_definitions = []
        self.refresh_flows_thread = threading.Thread(
            target=self._refresh_flows_thread_inner)
        self.refresh_flows_thread.daemon = True

    def token_updater(self, token):
        self.token = token

    def fetch(self, table, criteria, sort=None, start=None, end=None):
        """Fetch data by criteria

        The optional start and end parameters can be used to page the returned
        results.

        Args:
            table (str): The table to fetch from
            criteria (criteria): The criteria to match
            sort (list, optional): The fields to sort on
            start (int, optional):  The first row to return
            end (int, optional): The last row to return

        Returns:
            The list of matched records

        Examples:
            >>> slims.fetch("Content",
                            start_with("cntn_id", "DNA"),
                            sort = ["cntn_barCode"],
                            start = 10,
                            end = 20)

            Fetches content records that have an id that starts with DNA. The
            returned list is sorted by cntn_barCode (ascending). The first returned
            results is the has the 10th barcode and the last one is the 20th

            >>> slims.fetch("Content",
                            start_with("cntn_id", "DNA"),
                            sort = ["-cntn_barCode"])

            Fetches content records that have an id that starts with DNA. The
            returned list is sorted by cntn_barCode (descending).
        """
        if sort is None:
            sort = []
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

        Args:
            table (string): The table of the record
            pk (int): The primary key of the record

        Returns:
            A single record (or None)

        Examples:
            >>> slims.fetch_by_pk("Content", 1)
        """
        entities = self.slims_api.get_entities(table + "/" + str(pk))
        if len(entities) > 0:
            return entities[0]
        else:
            return None

    def add(self, table, values):
        """ Add a new record in slims

        Args:
            table (string): Table where the element need to be added.
            values (dict): The values of the new record

        Returns:
            The added record

        Examples:
            >>> slims.add("Content", {
                    "cntn_id", "ID",
                    "cntn_status", Status.PENDING,
                    "cntn_fk_contentType", 1
                })

            Adds a content record with id "ID" in status pending with the content type
            with primary key 1
        """
        response = self.slims_api.put(url=table, body=values)
        if response.status_code != 200:
            raise _SlimsApiException("Add failed: " + response.text)
        new_values = response.json()["entities"][0]
        return Record(new_values, self.slims_api)

    def add_flow(self, flow_id, name, usage, steps, testing=False, last_flow=True):
        """Add a new SLimsGate flow to the slims interface

        Note:
            Adding a slimsgate flow means your python script will continue
            executing until you shut it down.

        Args:
            flow_id (string): Technical identificator of the flow
            name(string): Displayed name of the the flow
            usage(string): Usage of the slimsgate flow
            steps(list step): The steps of the slimsgate flow
            testing(bool): Dry run=======
            last_flow(boolean): Defines if this is the last flow you will add (Default True)

        Examples:
            >>> def hello_world(flow_run):
                    print("Hello world")
            >>> slims.add_flow(
                    flow_id="helloWorld",
                    name="Make python say hello",
                    usage="CONTENT_MANAGEMENT",
                    steps=[
                        Step(
                            name="The step",
                            action=hello_world
                        )])
        """

        if not self.oauth:
            raise Exception('Python flows require oauth to be enabled')

        step_dicts = []
        i = 0
        for step in steps:
            url = flow_id + "/" + repr(i)
            step_dicts.append(step.to_dict(url))
            self.operations[url] = step
            i += 1

        flow = {'id': flow_id, 'name': name, 'usage': usage,
                'steps': step_dicts, 'pythonApiFlow': True}
        self.flow_definitions.append(flow)
        if self.token is None and not testing and last_flow:
            print("Visit " + self.slims_api.authorization_url())
            _flask_thread(self.local_port)
        else:
            self._register_flows([flow], False)

    def _handle_oauth_code(self, code):
        self.token = self.slims_api.fetch_token(code)
        if not self.refresh_flows_thread.is_alive():
            self.refresh_flows_thread.start()

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
                            + " (HTTP Response code: " + str(response.status_code) + ")")
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
        def refresh_flows(internal_scheduler):
            self._register_flows(self.flow_definitions, True)
            internal_scheduler.enter(
                60, 1, refresh_flows, (internal_scheduler,))

        scheduler = sched.scheduler(time.time, time.sleep)
        scheduler.enter(5, 1, refresh_flows, (scheduler,))
        scheduler.run()


class Record(object):
    """ A single record in SLims. Can be of any table, represents one row in the
    database

    Columns can be accessed as properties.

    Examples:
        >>> content = slims.fetch_by_pk("Content", 1)
            print(content.cntn_id.value)
    """

    def __init__(self, json_entity, slims_api):
        self.json_entity = json_entity
        self.slims_api = slims_api

        for json_column in json_entity["columns"]:
            column = Column(json_column)
            self.__dict__[column.name] = column

    def update(self, values):
        """ Updates this record

        Args:
            values (dict): Values to update

        Returns:
            The updated record

        Examples:
            >>> content = slims.fetch_by_pk("Content", 1)
                content.update({"cntn_id", "new id"})

            Fetches the content record with primary key 1 and changes
            its id to "new id"
        """
        url = self.table_name() + "/" + str(self.pk())
        response = self.slims_api.post(url=url, body=values)
        if response.status_code != 200:
            raise _SlimsApiException("Update failed: " + response.text)
        new_values = response.json()["entities"][0]
        return Record(new_values, self.slims_api)

    def remove(self):
        """
        Removes this record.
        """
        url = self.table_name() + "/" + str(self.pk())
        response = self.slims_api.delete(url=url)
        if response.status_code != 200:
            raise _SlimsApiException("Delete failed: " + response.text)

    def table_name(self):
        """
        Returns:
            The name of the table of this record
        """
        return self.json_entity["tableName"]

    def pk(self):
        """
        Returns:
            The primary key of this record
        """
        return self.json_entity["pk"]

    def attachments(self):
        """
        Returns:
            The attachments related to this record
        """
        return self.slims_api.get_entities(
            "attachment/" + self.json_entity["tableName"] + "/" + str(self.json_entity["pk"]))

    def add_attachment(self, name, byte_array):
        """Adds an attachment to a record (over HTTP).

        Args:
            name (string): The name of the attachment
            byte_array (byte array): The binary content of the attachment

        Returns:
            The primary key of the added attachment

        Examples:
            >>> content.add_attachment("test.txt", b"Hi from python")

            Adds a string as an attachment to a content record

            >>> with open(file_name, 'rb') as to_upload:
                    content.add_attachment("test.txt", to_upload.read())

            Uploads a file as an attachment in SLims
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
        Args:
            column_name (string): The name of the column

        Returns:
            A column of the record

        Examples:
            >>> print(content.column("cntn_id").value)
            >>> print(column.cntn_id.value)

        """
        return self.__dict__[column_name]

    def follow(self, link_name):
        """
        Follows an incoming or outgoing foreign key

        Args:
            link_name(string): field linking two tables.
                The links should start with a - (minus) if the link is incoming.

        Returns:
            One record (or None) when the link is outgoing
            A list of records when the link is incoming

        Examples:
            >>> content_type = slims.fetch_by_pk("Content", 1L)
                    .follow("cntn_fk_contentType")

            This fetches the content record with primary key 1 and then fetches
            its content type (one record).

            >>> results = slims.fetch_by_pk("Content", 1L)
                    .follow("-rslt_fk_content")

            This fetches the content record with primary key 1 and then fetches
            its results (a list of records)
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
    """ An extension of the Record class. Returned when the table of the
    record is Attachment."""

    def __init__(self, json_entity, slims_api):
        super(Attachment, self).__init__(json_entity, slims_api)

    def get_local_path(self):
        """
        Returns:
            The location of an attachment on disk
        Note:
            Only works when slims is defined with a repo_location
        """
        if self.slims_api.repo_location:
            return os.path.join(self.slims_api.repo_location, self.attm_path.value)
        else:
            raise RuntimeError("no repo_location configured")

    def download_to(self, location):
        """
        Downloads an attachment to a file on disk

        Args:
            location(string): The path on disk to download the file to

        Examples:
            >>> attachment.download_to("test.txt")
        """
        with open(location, 'wb') as destination:
            response = self.slims_api.get("repo/" + str(self.pk()))
            destination.write(response.content)


class Column(object):

    def __init__(self, json_column):
        self.__dict__.update(json_column)
