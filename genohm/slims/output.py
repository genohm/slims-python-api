import base64


def file_value(file_name):
    with open(file_name, 'rb') as output:
        return {'bytes': str(base64.b64encode(output.read())), 'fileName': output.name}
