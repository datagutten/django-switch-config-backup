====================
Switch config backup
====================

This is a django application to backup switch configs

It can download the config from the switch using SFTP or SCP, or it can login to the switch CLI and execute a command to upload the config.

The configs are saved in a git repository

Supported backup methods:

* Telnet and SSH CLI upload:
    * Cisco
* SCP fetch:
    * Cisco
* SFTP fetch:
    * HPE Aruba
    * Extreme Networks

Some switches need config changes to enable SFTP or SCP:

* HPE Aruba (SFTP):
    * `ip ssh filetransfer`
* Cisco (SCP):
    * `ip scp server enable`

Gitlist is required to show configs on web:

https://gitlist.org/

Quick start
-----------
1. Add "config_backup" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'config_backup',
    ]

2. Run `python manage.py migrate` to create the config_backup models.

3. Install Gitlist

4. Create a root folder for the repository folder and add it to Gitlists config

5. Create the repository folder

6.  Add the repository folder to settings.py with the key `BACKUP_PATH`

    Set BACKUP_URL to the path for CLI backup for Cisco (Optional)

7. In django admin console add common and/or switch specific username, password and backup type

7. Run `python manage.py config_backup [switch name]` to backup the config from a switch
