class FlowRun(object):

    def __init__(self, slims, index, data):
        self.slims = slims
        self.index = index
        self.data = data

    def log(self, message):
        body = {
            'index': self.index,
            'flowRunGuid': self.data["flowInformation"]["flowRunGuid"],
            'message': message
        }
        self.slims._post("external/log", body)
