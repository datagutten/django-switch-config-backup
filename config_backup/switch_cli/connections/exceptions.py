class UnexpectedResponse(Exception):
    """Device returned unexpected response"""
    payload: bytes = b''

    def __init__(self, message, payload: bytes = None):
        self.message = message
        self.payload = payload

    def __str__(self):
        return str(self.message)


class InvalidCommand(UnexpectedResponse):
    pass
    # def __init__(self, output, command):
    #     super(InvalidCommand, self).__init__('Invalid command: %s' % command)


class CLIConnectionError(Exception):
    pass
