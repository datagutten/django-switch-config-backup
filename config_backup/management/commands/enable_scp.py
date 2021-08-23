import datetime

from switchinfo.management.commands import SwitchBaseCommand

from config_backup.ConfigBackup import backup_options
from config_backup.switch_cli.get_connection import get_connection

now = datetime.datetime.now()


class Command(SwitchBaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('switch', nargs='+', type=str)

    def handle(self, *args, **cmd_options):
        for switch in self.handle_arguments(cmd_options):

            options = backup_options(switch)
            if options is None:
                continue
            try:
                cli = get_connection(switch.type, 'SSH')()
                cli.login(switch.ip, options.username, options.password, options.enable_password)
            except AttributeError:
                cli = get_connection(switch.type, 'Telnet')()
                cli.login(switch.ip, options.username, options.password, options.enable_password)

            if switch.type == 'Cisco':
                cli.command('configure terminal', '(config)#')
                cli.command('aaa authorization exec default local', '(config)#')
                cli.command('ip scp server enable', '(config)#')
                cli.command('exit', '#')
                cli.command('write memory', 'Building configuration')
            else:
                print(cli.command('configure', '(config)#'))
                if not cli.connection_type == 'SSH':
                    print(cli.command('ip ssh', '(config)#'))
                print(cli.command('ip ssh filetransfer', '(config)#', timeout=10))
                print(cli.command('write memory', '(config)#', timeout=10))
