import socket

import paramiko

from .Connection import Connection
from ..exceptions import UnexpectedResponse


class SSH(Connection):
    connection: paramiko.Channel
    connection_type = 'SSH'

    def connect(self, ip, username=None, password=None):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        try:
            client.connect(hostname=ip, username=username,
                           password=password,
                           look_for_keys=False,
                           allow_agent=False)
            self.connection = client.invoke_shell()
            self.connection.settimeout(self.timeout)
        except paramiko.SSHException as e:
            raise ConnectionError(e)
        except paramiko.ssh_exception.NoValidConnectionsError as e:
            raise ConnectionError(e)

    def set_timeout(self, timeout: int):
        self.timeout = timeout
        self.connection.settimeout(timeout)

    def read(self) -> bytes:
        # print('ready', self.connection.recv_ready())
        try:
            return self.connection.recv(9999)
        except socket.timeout as e:
            raise TimeoutError from e

    def ready(self) -> bool:
        return self.connection.recv_ready()

    def read_wait(self) -> bytes:
        response = b''
        while not self.ready():
            try:
                response += self.read()
            except TimeoutError:
                break
        return response

    def command(self, command, read_until=None, timeout=2) -> bytes:
        self.connection.send(command)
        self.set_timeout(timeout)
        return self.read_wait()
