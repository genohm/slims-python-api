import logging
from enum import Enum
from typing import Any

from .internal import _SlimsApi

logger = logging.getLogger('genohm.slims.flowrun')


class Status(Enum):
    """ Status of a flow run step """
    DONE = 1
    FAILED = 2


class FlowRun(object):
    def __init__(self, slims_api: _SlimsApi, index: str, data: dict[str, Any]):
        self.slims_api = slims_api
        self.index = index
        self.data = data

    def log(self, message: str) -> None:
        """
        Logs a message to Slims

        Args:
            message (string): the message to log

        Example:
            >>> def step_action(flow_run):
                    flow_run.log("Hello from python")
        """
        logger.info(message)
        body = {
            'index': self.index,
            'flowRunGuid': self.data["flowInformation"]["flowRunGuid"],
            'message': message
        }
        self.slims_api.post("external/log", body)

    def _update_status(self, status: Status) -> None:
        logger.info("Updating flowrun to status " + status.name)
        body = {
            'index': self.index,
            'flowRunGuid': self.data["flowInformation"]["flowRunGuid"],
            'status': status.name
        }
        self.slims_api.post("external/status", body)
