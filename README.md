# django-switch-config-backup
A django app to backup switch config

# Setup
* Add to INSTALLED_APPS: `config_backup.apps.ConfigBackupConfig`
* Set BACKUP_PATH to the git repository. There should be a parent folder that can be set as the root for gitlist

* Enable SFTP:
    * HPE Aruba: `ip ssh filetransfer`
    * HP ProCurve `ip ssh` and `ip ssh filetransfer`

* Setup gitlist:
apt-get install libapache2-mod-php
Enable mod_rewrite in apache