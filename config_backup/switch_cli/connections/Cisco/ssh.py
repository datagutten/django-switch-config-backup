from time import sleep

from ..common.ssh import SSH


class CiscoSSH(SSH):
    connection = None
    connection_type = 'SSH'

    def login(self, ip, username, password, enable_password):
        self.connect(ip, username, password)

        while not self.connection.recv_ready():
            sleep(3)

        out = self.connection.recv(9999)
        out = out.decode('ASCII')
        if out[-1] == '>':
            self.command('enable', 'Password:')
            self.command(enable_password, '#')
