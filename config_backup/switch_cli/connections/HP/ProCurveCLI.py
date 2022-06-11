import re

from config_backup.switch_cli.connections import common
from config_backup.switch_cli.connections.exceptions import CLIConnectionError, UnexpectedResponse


class ProCurveCLI(common.SwitchCli):
    def get_prompt(self, output: bytes):
        matches = re.search(r'.+;1H(.+[>#])', output.decode('utf-8'))
        if matches:
            self.prompt = matches.group(1)
        else:
            raise UnexpectedResponse('Unable to find prompt')

    def login(self, ip, username, password, enable_password):
        self.connection.connect(ip, username, password)

        response = self.connection.read_wait()

        if response.find(b'Press any key to continue') > -1:
            print('Press any key')
            if self.connection_type == 'telnet':
                response = self.command(b'\n', b'Username:')
            else:
                response = self.command(b'\n')

        if response.find(b'as operator') > -1:
            raise UnexpectedResponse('Logged in as operator')

        if response.find(b'Username:') > -1:
            self.command(username, b'Password:', update_prompt=False)
            try:
                self.command(password, '#')
            except UnexpectedResponse as e:
                if e.payload.find(b'Invalid password') > -1 or e.payload.find(
                        b'Authentication failed') > -1:
                    raise CLIConnectionError('Authentication failed')
        elif response.find(b'#') == -1:
            raise UnexpectedResponse('Login prompt not found', response)
        self.get_prompt(response)

    def save(self):
        return self.command('write memory', '(config)#', timeout=10)

    def configure(self) -> bytes:
        if not re.search(r'\((?:config|[a-z]+-.+?)\)', self.prompt):
            return self.command('configure', '(config)#')
        else:
            return b''

    def _configure_interface(self, interface: str) -> bytes:
        output = self.configure()
        output += self.command('interface %s' % interface, '(eth-%s)' % interface)
        return output

    def _configure_vlan(self, vlan: int) -> bytes:
        output = self.configure()
        output += self.command('vlan %s' % vlan, '(vlan-%d)' % vlan)
        return output

    def enable_scp(self):
        self.configure()
        if not self.connection_type == 'SSH':
            print('Enabling SSH')
            self.command('ip ssh', '(config)#')
        print('Enabling SCP')
        self.command('ip ssh filetransfer', '(config)#', timeout=10)
        self.save()

    def set_hostname(self, hostname: str):
        self.configure()
        self.command('hostname %s' % hostname, '(config)#')
        self.save()
