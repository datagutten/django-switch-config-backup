import datetime

from django.core.management.base import BaseCommand
from switchinfo.models import Switch

from config_backup.ConfigBackup import backup_options
from config_backup.switch_cli.get_connection import get_connection

now = datetime.datetime.now()


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('switch', nargs='+', type=str)

    def handle(self, *args, **cmd_options):
        if not cmd_options['switch'][0] == 'all':
            switches = Switch.objects.filter(name=cmd_options['switch'][0])
            print(switches)
        else:
            switches = Switch.objects.all()
        if not switches:
            print('No switches found')
            return

        for switch in switches:

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
