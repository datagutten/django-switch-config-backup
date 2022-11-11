from django.shortcuts import render

from .models import SwitchBackup


def backup_status(request):
    switches = SwitchBackup.objects.all()
    return render(request, 'config_backup/backup_status.html',
                  {'switches': switches, 'title': 'Backup status'})
