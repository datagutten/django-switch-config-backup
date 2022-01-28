from django.core.management.base import BaseCommand  # , CommandError
from switchinfo.models import Switch

from config_backup.ConfigBackup import backup_options, connect_cli
from config_backup.switch_cli.get_connection import get_cli


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('switch', nargs='+', type=str)
        parser.add_argument('interface', nargs=1, type=str)

    def handle(self, *args, **cmd_options):
        switch = Switch.objects.get(name=cmd_options['switch'][0])
        print(switch)

        if not switch:
            print('No switches found')
            return

        options = backup_options(switch)
        if options is None:
            return

        cli_class = get_cli(switch.type)
        if not hasattr(cli_class, 'poe_off'):
            print('Power cycling on %s is not supported' % switch.type)
            exit()

        cli = connect_cli(switch)
        cli.poe_off(cmd_options['interface'][0])
        cli.poe_on(cmd_options['interface'][0])
