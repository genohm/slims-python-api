from genohm.slims import Slims


class AFlowInPython(object):

    def execute(self):
        print "python was just called from slims :o"

    def name(self):
        return "remotePythonFlow"


slims = Slims("testSlims", "http://localhost:9999", "admin", "admin")
slims.register(AFlowInPython())
