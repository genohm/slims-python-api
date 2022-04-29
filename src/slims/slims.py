import logging
import sched
import threading
import time
from typing import Any, List, Optional

from flask import Flask, Response, jsonify, abort
from flask import request as flaskrequest

from .criteria import Criterion
from .internal import Record, _SlimsApi, _SlimsApiException
from .step import Step

app = Flask(__name__)
slims_instances: dict[str, 'Slims'] = {}
logger = logging.getLogger('genohm.slims.slims')
logging.basicConfig(level=logging.INFO)


@app.route("/<name>/<operation>/<step>", methods=["POST"])
def _start_step(name: str, operation: str, step: str) -> Response:
    data = flaskrequest.json
    if data is None:
        abort(400, description="Expected JSON data")
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
        return jsonify({})


@app.route("/<instance>/token", methods=["GET"])
def _token_validator(instance: str) -> str:
    slims_instances[instance]._handle_oauth_code(flaskrequest.args.get('code'))
    return 'Python instance "' + instance + '" registered'


def _flask_thread(port: int) -> None:
    app.run(port=port, host='0.0.0.0')


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
        request_params: Parameters to pass verbatim to requests when calling the REST API, e.g. verify='path/to/cert'
    """

    def __init__(self,
                 name: str,
                 url: str,
                 username: str = None,
                 password: str = None,
                 oauth: bool = False,
                 client_id: str = None,
                 client_secret: str = None,
                 repo_location: str = None,
                 local_host: str = "localhost",
                 local_port: int = 5000,
                 **request_params: Any):

        slims_instances[name] = self
        self.local_host = local_host
        self.local_port = local_port
        self.local_url = "http://" + self.local_host + \
            ":" + str(self.local_port) + "/"
        if username is not None and password is not None:
            self.slims_api = _SlimsApi(url, username, password, repo_location, **request_params)
        elif oauth:
            self.slims_api = _SlimsApi(url,
                                       "OAUTH",
                                       "oauth",
                                       repo_location,
                                       True,
                                       self.token_updater,
                                       self.local_url + name + "/token",
                                       client_id=client_id,
                                       client_secret=client_secret,
                                       **request_params)
            self.token: Optional[dict[str, Any]] = None
        else:
            raise Exception(
                "Either specify a username and a password or use oauth")

        self.name = name
        self.oauth = oauth
        self.operations: dict[str, Step] = {}
        self.flow_definitions: list[dict[str, Any]] = []
        self.refresh_flows_thread = threading.Thread(
            target=self._refresh_flows_thread_inner)
        self.refresh_flows_thread.daemon = True

    def token_updater(self, token: dict[str, Any]) -> None:
        self.token = token

    def fetch(self, table: str, criteria: Criterion, sort: list[str] = None,
              start: int = None, end: int = None) -> List[Record]:
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
        body: dict[str, Any] = {
            "sortBy": sort,
            "startRow": start,
            "endRow": end,
        }
        if criteria:
            body["criteria"] = criteria.to_dict()

        return self.slims_api.get_entities(table + "/advanced", body=body)

    def fetch_by_pk(self, table: str, pk: int) -> Optional[Record]:
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

    def add(self, table: str, values: dict[str, Any]) -> Record:
        """ Add a new record in slims

        Args:
            table (string): Table where the element need to be added.
            values (dict): The values of the new record

        Returns:
            The added record

        Examples:
            >>> slims.add("Content", {
                    "cntn_id", "ID",
                    "cntn_status", Status.PENDING.value,
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

    def add_flow(self, flow_id: str, name: str, usage: str, steps: list[Step],
                 testing: bool = False, last_flow: bool = True) -> None:
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

    def _handle_oauth_code(self, code: Optional[Any]) -> None:
        self.token = self.slims_api.fetch_token(code)
        if not self.refresh_flows_thread.is_alive():
            self.refresh_flows_thread.start()

    def _register_flows(self, flows: list[dict[str, Any]], is_reregister: bool) -> None:
        flow_ids = map(lambda flow: flow.get('id'), flows)
        verb = "re-register" if is_reregister else "register"

        try:
            instance = {'url': "http://" + self.local_host + ':' + str(self.local_port), 'name': self.name}
            body = {'instance': instance, 'flows': flows}
            response = self.slims_api.post("external/", body)

            if response.status_code == 200:
                logger.info("Successfully " + verb + "ed " + str(flow_ids))
            else:
                logger.info("Could not " + verb + " " + str(flow_ids)
                            + " (HTTP Response code: " + str(response.status_code) + ")")
                try:
                    logger.info("Reason: " + response.json()["errorMessage"])
                except Exception:
                    # Probably no json was sent
                    pass
        except Exception:
            logger.info("Could not " + verb + " flows " + str(flow_ids) + " trying again in 60 seconds")

    def _execute_operation(self, operation: str, step: str, data: dict[str, Any]) -> Any:
        from .flowrun import FlowRun
        flow_run = FlowRun(self.slims_api, step, data)
        output = self.operations[operation + "/" + str(step)].execute(flow_run)
        return output

    def _refresh_flows_thread_inner(self) -> None:
        def refresh_flows(internal_scheduler: sched.scheduler) -> None:
            self._register_flows(self.flow_definitions, True)
            internal_scheduler.enter(
                60, 1, refresh_flows, (internal_scheduler,))

        scheduler = sched.scheduler(time.time, time.sleep)
        scheduler.enter(5, 1, refresh_flows, (scheduler,))
        scheduler.run()
