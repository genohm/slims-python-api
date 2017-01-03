import base64


def file_value(file_name):
    """
        Opens the file with file_name and returns its content as a string.

        Args:
            file_name (string): Name of the file to read.
        Returns:
            (dic) with "bytes":value(String) and "fileName":value(String)
        """
    with open(file_name, 'rb') as output:
        return {'bytes': str(base64.b64encode(output.read())), 'fileName': output.name}
