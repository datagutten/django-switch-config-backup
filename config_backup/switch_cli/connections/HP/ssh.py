from time import sleep

from ..common.ssh import SSH
from ...utils import strip_output


class HpSSH(SSH):
    def login(self, ip, username, password, enable_password=None):
        self.connect(ip, username, password)

        self.connection.send("\n")
        self.connection.send("\n")
        while not self.connection.recv_ready():
            sleep(3)

        out = self.connection.recv(9999)
        out = out.decode('ASCII')
        print(strip_output(out))
