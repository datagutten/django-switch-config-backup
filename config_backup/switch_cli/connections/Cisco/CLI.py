import re

from ..common import SwitchCli
from ..exceptions import UnexpectedResponse


def get_prompt(output: bytes):
    matches = re.search(r'(.+[>#])$', output.decode('utf-8'))
    if matches:
        return matches.group(1)


class CiscoCLI(SwitchCli):
    def __init__(self, connection_type='telnet'):
        super().__init__(connection_type)

    def login(self, ip, username, password, enable_password):
        self.connection.connect(ip, username, password)
        output = self.connection.read_wait()

        if output.find(b'Username:') > -1:
            output = self.command(username, b'Password:')

        if output.find(b'Password:') > -1:
            try:
                self.command(password, b'>')
                self.command(b'enable', b'Password:')
                output = self.command(enable_password, b'#')
            except UnexpectedResponse as e:
                if e.payload.find(b'#') == -1:
                    raise e
        else:
            self.prompt = get_prompt(output)
            if not self.prompt:
                raise UnexpectedResponse('Unexpected initial output', output)

        self.prompt = get_prompt(output)

    def backup(self):
        print('Show running config')
        response = self.command('show running-config', read_until=b'--More--', timeout=5)
        print('Prompt', self.prompt)

        while response.decode('utf-8').find(self.prompt) == -1:
            print('More')
            response += self.command(' ', read_until=b'--More--', timeout=5)
            # response += self.connection.read()
            print('%d bytes' % len(response))
            print('Last 10:', response[-10:])
            print('Last', response[-1:1])
            print('Prompt find', response.decode('utf-8').find(self.prompt))

        response = re.sub(rb'\s--More--\s\x08+\s+\x08+', b'', response)
        return response

    def backup_copy(self, url):
        self.command('copy running-config %s' % url,
                     b'Address or name of remote host', b'?')
        self.command(b'\n', b'Destination filename', b'?')
        try:
            self.command(b'\n', b'#')
        except UnexpectedResponse as e:
            if e.payload.strip() == '':
                from time import sleep
                sleep(3)
            else:
                print(ord(e.payload.strip()[0]))
                raise e

    def enable_scp(self):
        self.command('configure terminal', '(config)#')
        self.command('aaa authorization exec default local', '(config)#')
        self.command('ip scp server enable', '(config)#')
        self.command('exit', '#')
        self.command('write memory', 'Building configuration')
