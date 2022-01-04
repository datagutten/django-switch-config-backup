import datetime

from django.core.management.base import BaseCommand
from switchinfo.SwitchSNMP.select import get_switch
from switchinfo.load_info import switch_info
from switchinfo.models import Switch

from config_backup.ConfigBackup import backup_options, connect_cli
from config_backup.switch_cli.get_connection import get_cli

now = datetime.datetime.now()


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('switch', nargs='+', type=str)
        parser.add_argument('hostname', nargs=1, type=str)

    def handle(self, *args, **cmd_options):
        print(cmd_options)
        switch = Switch.objects.get(ip=cmd_options['switch'][0])
        print(switch)

        if not switch:
            print('No switches found')
            return

        options = backup_options(switch)
        if options is None:
            return

        cli_class = get_cli(switch.type)
        if not hasattr(cli_class, 'set_hostname'):
            print('Hostname editing on %s is not supported' % switch.type)
            exit()

        cli = connect_cli(switch)
        cli.set_hostname(cmd_options['hostname'][0])
        device = get_switch(switch)
        print(switch_info.switch_info(device=device))
