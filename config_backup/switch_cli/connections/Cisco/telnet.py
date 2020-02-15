import socket

from ..exceptions import UnexpectedResponse
from ..common.telnet import Telnet


class CiscoTelnet(Telnet):
    connection = None
    connection_type = 'telnet'

    def login(self, ip, username, password, enable_password=None):
        if not enable_password:
            enable_password = password
        try:
            self.connect(ip)
            tn = self.connection
            self.connection.write(b"\n")
            output = tn.read_until(b'Password:', 2).decode('utf-8')

            if output.find('Username:') > -1:
                output = self.command(username, 'Password:')

            if output.find('Password:') > -1:
                try:
                    self.command(password, '>')
                    self.command('enable', 'Password:')
                    self.command(enable_password, '#')
                except UnexpectedResponse as e:
                    if e.payload.find('#') == -1:
                        raise e
            else:
                print('Unexpected output: "%s"' % output)
                return

            # self.command(password, '>')

        except socket.timeout:
            raise TimeoutError('Timout connecting to %s' % ip)
