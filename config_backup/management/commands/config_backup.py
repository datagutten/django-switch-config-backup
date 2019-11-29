import datetime


from django.core.management.base import BaseCommand

from switchinfo.models import Switch
from config_backup.git import Git
from config_backup import backup
from config_backup.ConfigBackup import backup_options

now = datetime.datetime.now()


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('switch', nargs='+', type=str)

    def handle(self, *args, **cmd_options):
        git = Git(backup.local_path)
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
                local_file = backup.backup(switch,
                                           options.connection_type,
                                           options.username,
                                           options.password,
                                           options.enable_password)
            except (TimeoutError, backup.BackupFailed, ValueError) as e:
                print(e)
                continue

            git.add(local_file)

        git.commit('Backup ' + cmd_options['switch'][0])
