from django.contrib import admin

# Register your models here.
from .models import SwitchBackupOption, CommonBackupOption


class BackupOptionAdmin(admin.ModelAdmin):
    list_display = ('switch', 'exclude', 'connection_type')


admin.site.register(SwitchBackupOption, BackupOptionAdmin)


class CommonBackupOptionAdmin(admin.ModelAdmin):
    list_display = ('type', 'connection_type')


admin.site.register(CommonBackupOption, CommonBackupOptionAdmin)
