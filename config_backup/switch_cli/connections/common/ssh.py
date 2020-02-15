import time

import paramiko

from .SwitchCli import SwitchCli
from ..exceptions import UnexpectedResponse


class SSH(SwitchCli):
    connection_type = 'SSH'

    def connect(self, ip, username, password):
        self.connection = paramiko.SSHClient()
        self.connection.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        self.connection.connect(hostname=ip, username=username, password=password, look_for_keys=False)
        self.connection = self.connection.invoke_shell()

    def command(self, cmd, expected_response=None, timeout=2):
        self.connection.send(cmd + '\n')
        while not self.connection.recv_ready():
            time.sleep(3)

        out = self.connection.recv(9999)
        output = out.decode("ascii")
        print(output)


        # stdin, stdout, stderr = self.connection.exec_command(cmd)
        # print(stdout)
        # output = stdout.read().decode("utf-8")
        # print(output)
        # print(output.find(expected_response))

        if expected_response and output.find(expected_response) == -1:
            raise UnexpectedResponse(
                'Unexpected response: "%s", expected "%s"' %
                (output, expected_response), output)
        else:
            return output

