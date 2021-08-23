import datetime

from switchinfo.management.commands import SwitchBaseCommand

from switchinfo.models import Switch
from config_backup.git import Git
from config_backup import backup
from config_backup.ConfigBackup import backup_options

now = datetime.datetime.now()


class Command(SwitchBaseCommand):
    def handle(self, *args, **cmd_options):
        backup_success = False
        git = Git(backup.local_path)
        switch: Switch
        for switch in self.handle_arguments(cmd_options):

            options = backup_options(switch)
            if options is None:
                continue

            try:
                local_file = backup.backup(switch,
                                           options.connection_type,
                                           options.username,
                                           options.password,
                                           options.enable_password)
            except (TimeoutError, ValueError) as e:
                print(e)
                continue
            except backup.BackupFailed as e:
                print('Backup failed: ' + str(e))
                continue
            backup_success = True
            git.add(local_file)

        if backup_success:
            git.commit('Backup ' + cmd_options['switch'][0])
