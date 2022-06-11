import re

from config_backup.exceptions import BackupFailed
from ..common import SwitchCli
from ..exceptions import UnexpectedResponse


class CiscoCLI(SwitchCli):
    def __init__(self, connection_type='telnet'):
        super().__init__(connection_type)

    def get_prompt(self, output: bytes):
        matches = re.search(r'(.+(?:[>#]|\(config.*?\)))$', output.decode('utf-8'))
        if matches:
            self.prompt = matches.group(1)
        else:
            raise UnexpectedResponse('Unable to find prompt', output)

    def login(self, ip, username, password, enable_password):
        self.connection.connect(ip, username, password)
        output = self.connection.read_wait()

        if output.find(b'Username:') > -1:
            output = self.command(username, b'Password:')

        if output.find(b'Password:') > -1:
            try:
                self.command(password, b'>', update_prompt=False)
                self.command(b'enable', b'Password:', update_prompt=False)
                output = self.command(enable_password, b'#')
            except UnexpectedResponse as e:
                if e.payload.find(b'#') == -1:
                    raise e
        else:
            self.get_prompt(output)
            if not self.prompt:
                raise UnexpectedResponse('Unexpected initial output', output)

        if self.prompt[-1] == '>':
            self.command(b'enable', b'Password:', update_prompt=False)
            output = self.command(enable_password, b'#')

        self.get_prompt(output)

    def save(self):
        command = 'write memory'
        if self.prompt.find('(config') > -1:
            command = 'do %s' % command

        return self.command(command, '[OK]', timeout=15, update_prompt=False)

    def backup(self):
        print('Show running config')
        response = self.command('show running-config', read_until=b'--More--', timeout=5,
                                update_prompt=False)

        while response.decode('utf-8').find(self.prompt) == -1:
            response += self.command(' ', read_until=b'--More--', timeout=5, update_prompt=False)
            # response += self.connection.read()
            print('%d bytes\r' % len(response))
            # print('Last 10:', response[-10:])
            # print('Last', response[-1:1])
            # print('Prompt find', response.decode('utf-8').find(self.prompt))

        response = re.sub(rb'\s--More--\s\x08+\s+\x08+', b'', response)
        response = response.replace(b'\r', b'')
        return response

    def backup_copy(self, url):
        if self.prompt[-1] != '#':
            raise BackupFailed('Not write enabled')

        self.command('copy running-config %s' % url,
                     b'Address or name of remote host', b'?', update_prompt=False)
        self.command(b'\n', b'Destination filename', b'?', update_prompt=False)
        try:
            response = self.command(b'\n', b'#', decode=True, timeout=15)
            matches = re.search(r'([0-9]+) bytes copied', response)
            if not matches:
                raise BackupFailed(response.strip())
            else:
                return response.strip()
        except UnexpectedResponse as e:
            if e.payload.strip() == '':
                from time import sleep
                sleep(3)
            else:
                raise e

    def enable_scp(self):
        output = self.prompt
        output += self.command('configure terminal', '(config)#')
        output += self.command('aaa authorization exec default local', '(config)#')
        output += self.command('ip scp server enable', '(config)#')
        output += self.command('exit', '#')
        output += self.save()
        return output

    def poe_on(self, interface) -> str:
        output = self.prompt
        output += self.command('conf t', '(config)', decode=True)
        output += self.command('interface %s' % interface, '(config-if)', decode=True)
        output += self.command('power inline auto', '(config-if)', decode=True)
        return output

    def poe_off(self, interface) -> str:
        output = self.prompt
        output += self.command('conf t', '(config)', decode=True)
        output += self.command('interface %s' % interface, '(config-if)', decode=True)
        output += self.command('power inline never', '(config-if)', decode=True)
        return output

    def poe_cycle(self, interface) -> str:
        output = self.prompt
        output += self.command('conf t', '(config)', decode=True)
        output += self.command('interface %s' % interface, '(config-if)', decode=True)
        output += self.command('power inline never', '(config-if)', decode=True)
        output += self.command('power inline auto', '(config-if)', decode=True)
        return output
