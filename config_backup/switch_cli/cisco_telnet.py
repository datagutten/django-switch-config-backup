import telnetlib
import socket


class UnexpectedResponse(Exception):
    """Device returned unexpected response"""
    def __init__(self, message, payload=None):
        self.message = message
        self.payload = payload

    def __str__(self):
        return str(self.message)


class CiscoTelnet:
    connection = None
    connection_type = 'telnet'

    def command(self, cmd, expected_response=None, read_until=None):
        # print('Running command %s' % cmd)
        self.connection.write(cmd.encode('utf-8'))
        self.connection.write(b"\n")
        if expected_response:
            if not read_until:
                read_until = expected_response
            response = self.connection.read_until(read_until.encode('utf-8'), timeout=2)
            output = response.decode('utf-8')
            if output.find(expected_response) == -1:
                raise UnexpectedResponse(
                    'Unexpected response: "%s", expected "%s"' %
                    (output, expected_response), output)
        else:
            return self.connection.read_very_eager().decode('utf-8')

        return output

    def login(self, ip, username, password, enable_password=None):
        if not enable_password:
            enable_password = password
        try:
            tn = telnetlib.Telnet(ip, timeout=5)
            self.connection = tn
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
