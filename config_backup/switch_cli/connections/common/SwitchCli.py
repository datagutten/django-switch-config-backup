from abc import ABC

from .Connection import Connection
from .ssh import SSH
from .telnet import Telnet
from ..exceptions import UnexpectedResponse


class SwitchCli(ABC):
    connection: Connection
    connection_type: str
    _telnet = Telnet
    _ssh = SSH
    prompt: str

    def __init__(self, connection_type='telnet'):
        self.connection_type = connection_type
        if connection_type == 'telnet':
            self.connection = self._telnet()
        elif connection_type == 'ssh':
            if self._ssh:
                self.connection = self._ssh()
            else:
                print('SSH not available for %s, falling back to telnet' % self)
                self.connection_type = 'telnet'
                self.connection = self._telnet()
        else:
            raise Exception('Invalid CLI connection type: %s' % connection_type)

    def command(self, command, expected_response=None, read_until=None, timeout=2, decode=False):
        if type(command) == str:
            command = command.encode('utf-8')
        if type(expected_response) == str:
            expected_response = expected_response.encode('utf-8')
        if type(read_until) == str:
            read_until = read_until.encode('utf-8')

        self.connection.set_timeout(timeout)
        if command != b' ' and command != b'\n':
            command += b"\n"

        if not read_until and expected_response:
            read_until = expected_response

        response = self.connection.command(command, read_until, timeout)

        if expected_response and response.find(expected_response) == -1:
            raise UnexpectedResponse(
                'Unexpected response: "%s", expected "%s"' % (
                    response.decode('utf-8'),
                    expected_response),
                response)

        if decode:
            return response.decode('utf-8')
        else:
            return response

    def login(self, ip, username, password, enable_password):
        raise NotImplementedError
