from django.db import models
from switchinfo.models import Switch

connection_types = [['SSH', 'SSH'], ['Telnet', 'Telnet'], ['SCP', 'SCP'], ['SFTP', 'SFTP']]


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
    types = Switch.objects.order_by('type').values('type').distinct()
    types = types.values_list('type', flat=True)

    return zip(types, types)


class CommonBackupOption(models.Model):
    type = models.CharField(max_length=50, choices=switch_types(), unique=True)
    username = models.CharField(blank=True, null=True, max_length=50)
    password = models.CharField(blank=True, null=True, max_length=50)
    enable_password = models.CharField(blank=True, null=True, max_length=50)
    connection_type = models.CharField(choices=connection_types, max_length=50)

    def __str__(self):
        return '%s %s' % (self.type, self.connection_type)
