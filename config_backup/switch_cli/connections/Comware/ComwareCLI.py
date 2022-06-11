import re

from config_backup.switch_cli.connections import common
from config_backup.switch_cli.connections.exceptions import InvalidCommand, UnexpectedResponse


def normalize_interface(interface: str):
    matches = re.search(r'(\w+Ethernet)\s?([0-9/]+)', interface)
    if not matches:
        raise UnexpectedResponse('Unable to parse interface name')
    return matches.group(1) + matches.group(2)


class ComwareCLI(common.SwitchCli):
    def get_prompt(self, response: bytes):
        matches = re.search(r'([<\[].+[>\]])', response.decode('utf-8'))
        if not matches:
            raise UnexpectedResponse('Unable to find prompt in "%s"' % response.decode('utf-8'),
                                     response)
        self.prompt = matches.group(1)

    def command(self, command: str, expected_response=None, read_until=None, timeout=2,
                decode=False, update_prompt=True):
        try:
            return super().command(command, expected_response, read_until, timeout,
                                   decode, update_prompt)
        except UnexpectedResponse as e:
            if e.payload.find(b'Unrecognized command found') > -1:
                raise InvalidCommand('Unrecognized command: "%s"' % command,
                                     e.payload)
            else:
                raise e

    def login(self, ip, username, password, enable_password=None):
        self.connection.connect(ip, username, password)
        response = self.connection.read_wait()

        if not response:
            raise UnexpectedResponse(response)
        if response.find(b'Username:') > -1:
            self.command(username, b'Password:')
            self.prompt = self.command(password, '>', decode=False).strip()
        else:
            self.prompt = get_prompt(response)

    def save(self):
        print('Saving configuration')
        self.command('save', 'Are you sure')
        self.command('Y', 'Please input the file name')
        self.command('\n', 'overwrite')
        self.command('Y', 'Configuration is saved to device successfully.', timeout=10)

    def backup(self):
        self.connection.read()
        try:
            response = self.command('display current-configuration', '---- More ----')
        except UnexpectedResponse as e:
            if e.payload.find(b'Unrecognized command found') > -1:
                self.enable_cmd()
                response = self.command('display current-configuration', '---- More ----')
            else:
                raise e

        start = response.find(b'display current-configuration') + len(
            'display current-configuration')
        response = response[start:]

        while response.find(self.prompt) == -1:
            response += self.command(' ', read_until='---- More ----')

        response = response.replace(b'  ---- More ----', b'')
        response = re.sub(rb'\x1b\[42D\s+\x1b\[42D', b'', response)
        response = re.sub(rb'\x1b\[16D\s+\x1b\[16D', b'', response)
        return response

    def system_view(self):
        if self.prompt[0] == '[':
            return  # Already in system-view

        try:
            self.command('system-view', ']')
        except InvalidCommand:
            self.enable_cmd()
            self.command('system-view', ']')

    def enable_scp(self):
        self.system_view()
        print('Enabling SFTP server')
        try:
            self.command('sftp server enable', 'SFTP server has been enabled.')
        except UnexpectedResponse as e:
            if e.payload.find(b'Start SFTP server') == -1:
                raise e

        print('Setting SFTP authentication')
        try:
            self.command('ssh user admin authentication-type password')
            self.command('ssh user admin service-type sftp')
        except UnexpectedResponse:
            self.command('ssh user admin service-type sftp authentication-type password', ']')
        print('Creating RSA key pair')
        response = self.command('public-key local create rsa', timeout=15)
        if response.find(b'Warning: The local key pair already exist.') > -1:
            self.command('N')
        else:
            print('RSA response: ', response.decode('utf-8'))

        self.save()

    def enable_cmd(self):
        self.command('_cmdline-mode on', 'All commands can be displayed and executed')
        self.command('Y', 'Please input password:')
        # print('Password prompt: ', response2.decode('utf-8'))
        response = self.command('512900', self.prompt)
        if response.find(b'Unrecognized command found') > -1:
            raise UnexpectedResponse('Invalid password response: "%s"' % response.decode('utf-8'),
                                     response)

    def ntp_server(self, address):
        return self.command('ntp-service unicast-peer %s' % address)

    def poe_off(self, interface) -> str:
        self.system_view()
        output = self.prompt
        response = self.command('interface %s' % interface, 'Ethernet')
        output += response.decode()
        output += self.command('undo poe enable')
        return output

    def poe_on(self, interface) -> str:
        self.system_view()
        output = self.prompt
        interface = normalize_interface(interface)
        if interface not in self.prompt:
            response = self.command('interface %s' % interface, 'Ethernet')
            output += response.decode()
        output += self.command('poe enable')
        return output
