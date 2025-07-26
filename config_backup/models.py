import datetime
import os.path

from django.conf import settings
from django.db import DatabaseError, models
from switchinfo.models import Switch

from .exceptions import BackupFailed

connection_types = [['SSH', 'SSH'], ['Telnet', 'Telnet'], ['SCP', 'SCP'], ['SFTP', 'SFTP'],
                    ['http', 'http(s)']]


class SwitchBackupOption(models.Model):
    switch = models.OneToOneField(Switch, on_delete=models.CASCADE, related_name='backup_settings')
    exclude = models.BooleanField(help_text='Do not backup switch', default=False)
    username = models.CharField(blank=True, null=True, max_length=50)
    password = models.CharField(blank=True, null=True, max_length=50)
    enable_password = models.CharField(blank=True, null=True, max_length=50)
    connection_type = models.CharField(choices=connection_types, blank=True, null=True, max_length=50)

    def __str__(self):
        return str(self.switch)


def switch_types():
    try:
        types = Switch.objects.order_by('type').values('type').distinct()
        types = types.values_list('type', flat=True)
        return zip(types, types)
    except DatabaseError:
        return {}


class CommonBackupOption(models.Model):
    type = models.CharField(max_length=50, unique=True)
    username = models.CharField(blank=True, null=True, max_length=50)
    password = models.CharField(blank=True, null=True, max_length=50)
    enable_password = models.CharField(blank=True, null=True, max_length=50)
    connection_type = models.CharField(choices=connection_types, max_length=50)

    def __str__(self):
        return '%s %s' % (self.type, self.connection_type)


class SwitchBackup(Switch):
    class Meta:
        proxy = True

    def backup_file(self):
        if not settings.BACKUP_PATH:
            return
        file = os.path.join(settings.BACKUP_PATH, self.name)
        if os.path.exists(file):
            return file

    def backup_time(self):
        file = self.backup_file()
        if file:
            timestamp = os.path.getmtime(file)
            return datetime.datetime.fromtimestamp(timestamp)

    def backup_options(self):
        from .ConfigBackup import backup_options
        try:
            return backup_options(self)
        except BackupFailed:
            pass

    def gitlist_url(self):
        return settings.BACKUP_WEB_BASE + self.name
