import datetime

from switchinfo.management.commands import SwitchBaseCommand
from switchinfo.models import Switch

import config_backup.exceptions
from config_backup import backup
from config_backup.ConfigBackup import backup_options
from config_backup.git import Git

now = datetime.datetime.now()


class Command(SwitchBaseCommand):
    def handle(self, *args, **cmd_options):
        backup_success = False
        git = Git(backup.local_path)
        switch: Switch
        for switch in self.handle_arguments(cmd_options):
            try:
                options = backup_options(switch)
                local_file = backup.backup(switch,
                                           options.connection_type,
                                           options.username,
                                           options.password,
                                           options.enable_password)
            except (TimeoutError, ValueError) as e:
                print(e)
                continue
            except config_backup.exceptions.BackupFailed as e:
                print('Backup failed: ' + str(e))
                continue
            backup_success = True
            git.add(local_file)

        if backup_success:
            git.commit('Backup ' + cmd_options['switch'])
