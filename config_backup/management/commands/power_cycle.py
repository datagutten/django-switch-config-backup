from django.core.management.base import BaseCommand, CommandError
from switchinfo.models import Interface, Switch

from config_backup.ConfigBackup import backup_options, connect_cli
from config_backup.switch_cli.connections.common import SwitchCli
from config_backup.switch_cli.connections.exceptions import CLIConnectionError


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('switch', nargs='+', type=str)
        parser.add_argument('interface', nargs=1, type=str)

    def handle(self, *args, **cmd_options):
        try:
            switch = Switch.objects.get(name=cmd_options['switch'][0])
        except Switch.DoesNotExist:
            raise CommandError('No switch named %s' % cmd_options['switch'][0])
        try:
            interface_obj = switch.interfaces.get(interface=cmd_options['interface'][0])
        except Interface.DoesNotExist:
            raise CommandError(
                'No interface named %s on %s' % (cmd_options['interface'][0], switch))

        print(switch)

        if not switch:
            print('No switches found')
            return

        options = backup_options(switch)
        if options is None:
            return

        cli: SwitchCli = connect_cli(switch)
        try:
            print(cli.poe_cycle(interface_obj.interface))
        except NotImplementedError:
            raise CommandError('Power cycling on %s is not supported' % switch.type)
        except CLIConnectionError as e:
            raise CommandError(e)
