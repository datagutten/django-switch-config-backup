from abc import ABC

from .Connection import Connection

try:
    from .ssh import SSH
except ImportError:
    SSH = None
try:
    from .telnet import Telnet
except ImportError:
    Telnet = None

from ..exceptions import UnexpectedResponse


class SwitchCli(ABC):
    connection: Connection
    connection_type: str
    _telnet = Telnet
    _ssh = SSH
    prompt: str

    def __init__(self, connection_type='telnet'):
        self.connection_type = connection_type.lower()
        if self.connection_type == 'telnet':
            self.connection = self._telnet()
        elif self.connection_type in ['ssh', 'scp', 'sftp']:
            if self._ssh:
                self.connection = self._ssh()
            else:
                print('SSH not available for %s, falling back to telnet' % self)
                self.connection_type = 'telnet'
                self.connection = self._telnet()
        else:
            raise Exception('Invalid CLI connection type: %s' % connection_type)

    @staticmethod
    def strip_control_chars(data: bytes) -> bytes:
        return data

    def get_prompt(self, output: bytes):
        raise NotImplementedError()

    def command(self, command, expected_response=None, read_until=None, timeout=2,
                decode=False, update_prompt=True, negate=False):
        if type(command) == str:
            command = command.encode('utf-8')
        if type(expected_response) == str:
            expected_response = expected_response.encode('utf-8')
        if type(read_until) == str:
            read_until = read_until.encode('utf-8')

        self.connection.set_timeout(timeout)
        if command != b' ' and command != b'\n':
            command += b"\n"
        if negate:
            command = b'no %s' % command

        if not read_until and expected_response:
            read_until = expected_response

        response = self.connection.command(command, read_until, timeout)

        if expected_response and response.find(expected_response) == -1:
            raise UnexpectedResponse(
                'Unexpected response: "%s", expected "%s"' % (
                    self.strip_control_chars(response).decode('utf-8'),
                    expected_response),
                response)

        if update_prompt:
            try:
                self.get_prompt(response)
            except NotImplementedError:
                pass

        if decode:
            return response.decode('utf-8')
        else:
            return response

    def login(self, ip, username, password, enable_password):
        raise NotImplementedError

    def save(self) -> bytes:
        """
        Save running configuration to flash
        """
        raise NotImplementedError()

    def backup(self) -> bytes:
        """
        Get running config from CLI
        :return: Config as bytes
        """
        raise NotImplementedError

    def backup_copy(self, url: str) -> bytes:
        """
        Copy running config to specified URL
        :param url: URL to copy config to
        :return: CLI output
        """
        raise NotImplementedError

    def enable_scp(self) -> bytes:
        """
        Enable SCP server
        :return: CLI output
        """
        raise NotImplementedError

    def set_hostname(self, hostname: str) -> bytes:
        """
        Set switch hostname
        :param hostname: Hostname
        :return: CLI output
        """
        raise NotImplementedError

    def syslog(self, server: str, remove=False) -> bytes:
        """
        Add or remove a syslog server
        :param server: Syslog server address
        :param remove: Remove the syslog server
        :return: CLI output
        """
        raise NotImplementedError()

    def ntp_server(self, server: str, remove=False):
        """
        Add or remove an NTP server
        :param server: NTP server address
        :param remove: Remove the NTP server
        :return: CLI output
        """
        raise NotImplementedError()

    def poe_off(self, interface) -> bytes:
        """
        Disable PoE on the given interface
        :param interface: Interface name
        :return: CLI output
        """
        raise NotImplementedError

    def poe_on(self, interface) -> bytes:
        """
        Enable PoE on the given interface
        :param interface: Interface name
        :return: CLI output
        """
        raise NotImplementedError

    def poe_cycle(self, interface) -> str:
        """
        Disable and enable PoE on the given interface
        :param interface: Interface name
        :return: CLI output
        """
        output = self.poe_off(interface)
        output += self.poe_on(interface)
        return output.decode('utf8')

    def interface_name(self, interface: str, name: str) -> bytes:
        raise NotImplementedError

    def vlan_name(self, vlan: int, name: str) -> bytes:
        """
        Set vlan name and add the vlan to the switch
        :param vlan: vlan number
        :param name: vlan name
        :return: CLI output
        """
        raise NotImplementedError()

    def untagged_vlan(self, interface: str, vlan: int):
        """
        Set an interface as an access port
        :param interface: Interface name
        :param vlan: vlan number
        :return: CLI output
        """
        raise NotImplementedError()

    def tagged_vlan(self, interface: str, vlan: int):
        """
        Add a tagged vlan to an interfaces
        :param interface: Interface name
        :param vlan: Vlan number
        :return: CLI output
        """
        raise NotImplementedError()

    def snmp(self, community='public', permission='RO', remove=False):
        """
        Enable SNMP, set community with permission and optionally access list
        :param community: SNMP Community
        :param permission: Permission (RO or RW)
        :param remove: Remove the community
        :return:
        """
        pass
