class Step(object):

    def __init__(self, name, action, hidden=False, input=[], output=[]):
        self.action = action
        self.name = name
        self.hidden = hidden
        self.input = input
        self.output = output

    def to_dict(self, route_id):
        return {
            'hidden': self.hidden,
            'name': self.name,
            'input': {
                'parameters': self.input
            },
            'process': {
                'async': False,
                'route': route_id,
            },
            'output': {
               'parameters': self.output
            },
        }

    def action(self):
        return self.action


def text_input(name, label):
    return {'name': name, 'label': label, 'type': 'STRING'}


def file_output():
    return {'name': 'file', 'type': 'FILE'}
