import socket
import telnetlib

from .SwitchCli import SwitchCli
from ..exceptions import UnexpectedResponse


class Telnet(SwitchCli):
    connection_type = 'telnet'

    def connect(self, ip, username=None, password=None):
        try:
            print('Connecting to %s' % ip)
            tn = telnetlib.Telnet(ip, timeout=5)
        except socket.timeout:
            raise TimeoutError('Timout connecting to %s' % ip)
        self.connection = tn

    def command(self, cmd, expected_response=None, read_until=None, timeout=2):
        # print('Running command %s' % cmd)
        self.connection.write(cmd.encode('utf-8'))
        self.connection.write(b"\n")
        if expected_response:
            if not read_until:
                read_until = expected_response
            response = self.connection.read_until(read_until.encode('utf-8'),
                                                  timeout=timeout)
            output = response.decode('utf-8')
            if output.find(expected_response) == -1:
                raise UnexpectedResponse(
                    'Unexpected response: "%s", expected "%s"' %
                    (output, expected_response), output)
        else:
            return self.connection.read_very_eager().decode('utf-8')

        return output
