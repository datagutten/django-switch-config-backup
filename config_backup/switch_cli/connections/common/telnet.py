import socket
import telnetlib

from .Connection import Connection


class Telnet(Connection):
    connection_type = 'telnet'
    connection: telnetlib.Telnet

    def connect(self, ip, username=None, password=None):
        try:
            print('Connecting to %s using telnet' % ip)
            tn = telnetlib.Telnet(ip, timeout=5)
        except socket.timeout:
            raise TimeoutError('Timout connecting to %s' % ip)
        self.connection = tn

    def read(self) -> bytes:
        return self.connection.read_very_eager()

    def read_until(self, match: bytes) -> bytes:
        return self.connection.read_until(match, self.timeout)

    def command(self, cmd: bytes, read_until: bytes = None,
                timeout=2) -> bytes:
        # print('Running telnet command %s, expecting %s' % (cmd, expected_response))
        self.connection.write(cmd)

        if read_until:
            return self.read_until(read_until)
        else:
            return self.read_wait()
