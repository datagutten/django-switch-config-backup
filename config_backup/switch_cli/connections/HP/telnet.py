from time import sleep

from ..common.telnet import Telnet
from ..exceptions import UnexpectedResponse
from ...utils import strip_output


class HPTelnet(Telnet):
    output_log = None

    def __init__(self):
        self.output_log = open('hp_output.txt', 'w')

    def login(self, ip, username, password, enable_password=None):
        try:
            self.connect(ip)
            tn = self.connection
            self.connection.write(b"\n")
            self.connection.write(b"\n")
            # self.connection.write(b"\n")
            sleep(1)

            output = tn.read_until(b'Press any key to continue',
                                   2).decode('utf-8')
            output += tn.read_until(b':', 2).decode('utf-8')
            # output += tn.read_all().decode('utf-8')
            # matches = re.search(r'(.+)$', output)
            output = strip_output(output)
            output = output.strip().split("\n")[-1]
            # output = self.connection.read_very_eager().decode('utf-8')
            self.output_log.write(output + "\n-First response--\n")
            check = output.strip()
            if check[-1] == '>':
                output = self.command('enable', 'Username:')

            # Any key expected
            if output.find('Press any key to continue') > -1:
                output = self.command('a', 'Username:')
                self.output_log.write(
                    output + "\n-Any key response, username expected--\n")
                sleep(1)

            if output.find('Username:') > -1:
                sleep(1)
                output = self.command(username, 'Password:')
                self.output_log.write(
                    output + "\n-Username response, password expected--\n")
                sleep(1)

            if output.find('Password:') > -1:
                output = self.command(password, '#')
                self.output_log.write(
                    output + "\n-Password response, # expected--\n")
                sleep(1)

            if output.find('#') == -1 and output.find('>') == -1:
                raise UnexpectedResponse('Prompt not found', output)

        except UnexpectedResponse as e:
            self.output_log.write(e.payload + "\n-Unexpected response--\n")
            if e.payload.find('#') == -1 and e.payload.find('>') == -1:
                raise e

        self.output_log.close()
