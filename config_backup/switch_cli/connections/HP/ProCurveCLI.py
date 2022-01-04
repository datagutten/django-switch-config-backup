from config_backup.switch_cli.connections import common
from config_backup.switch_cli.connections.exceptions import UnexpectedResponse


class ProCurveCLI(common.SwitchCli):
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
            print('Username prompt')
            self.command(username, b'Password:')
            try:
                self.command(password, '#')
            except UnexpectedResponse as e:
                if e.payload.find(b'Invalid password') > -1:
                    e.message = 'Invalid password'
                raise e
        elif response.find(b'#') == -1:
            print('response bad', response)
            raise UnexpectedResponse('Login prompt not found')

    def save(self):
        print('Saving configuration')
        self.command('write memory', '(config)#', timeout=10)

    def enable_scp(self):
        self.command('configure', '(config)#')
        if not self.connection_type == 'SSH':
            print('Enabling SSH')
            self.command('ip ssh', '(config)#')
        print('Enabling SCP')
        self.command('ip ssh filetransfer', '(config)#', timeout=10)
        self.save()

    def set_hostname(self, hostname: str):
        self.command('configure', '(config)#')
        self.command('hostname %s' % hostname, '(config)#')
        # TODO: Update self.prompt with new name
        self.save()
