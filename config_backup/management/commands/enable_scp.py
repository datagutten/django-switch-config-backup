import datetime
import socket

from switchinfo.management.commands import SwitchBaseCommand

from config_backup.ConfigBackup import connect

now = datetime.datetime.now()


class Command(SwitchBaseCommand):
    def handle(self, *args, **cmd_options):
        for switch in self.handle_arguments(cmd_options):
            print('Enabling SCP on %s switch %s' % (switch.type, switch))
            try:
                cli = connect(switch, 'ssh')
            except (ConnectionError, socket.timeout):
                cli = connect(switch, 'telnet')

            cli.enable_scp()
