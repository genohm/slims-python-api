import threading
import logging
import traceback

from .flowrun import Status

logger = logging.getLogger('genohm.slims.step')


class Step(object):

    def __init__(self, name, action, async=False, hidden=False, input=[], output=[]):
        self.action = action
        self.name = name
        self.hidden = hidden
        self.input = input
        self.output = output
        self.async = async

    def to_dict(self, route_id):
        return {
            'hidden': self.hidden,
            'name': self.name,
            'input': {
                'parameters': self.input
            },
            'process': {
                'asynchronous': self.async,
                'route': route_id,
            },
            'output': {
               'parameters': self.output
            },
        }

    def execute(self, flow_run):
        if self.async:
            logger.info("Starting to run step %s asynchronously", self.name)
            return self._execute_async(flow_run)
        else:
            logger.info("Starting to run step %s synchronously", self.name)
            return self._execute_inner(flow_run)

    def _execute_async(self, flow_run):
        thr = threading.Thread(target=self._execute_inner, args=[flow_run])
        thr.start()

    def _execute_inner(self, flow_run):
        try:
            value = self.action(flow_run)
            flow_run.update_status(Status.DONE)
            logger.info("Done running step %s", self.name)
            return value
        except Exception:
            flow_run.log(traceback.format_exc())
            flow_run.update_status(Status.FAILED)
            logger.info("Failed running step %s", self.name)
            raise StepExecutionException


class StepExecutionException(Exception):
    pass


def text_input(name, label):
    return {'name': name, 'label': label, 'type': 'STRING'}


def file_output():
    return {'name': 'file', 'type': 'FILE'}
