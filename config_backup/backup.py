import subprocess
import os
from django.conf import settings

from .switch_cli.connections.exceptions import UnexpectedResponse
from .switch_cli.get_connection import get_connection

local_path = settings.BACKUP_PATH


class BackupFailed(Exception):
    """Exception raised when backup fails"""
    pass


def backup_file(switch):
    """
    Get backup file name with path
    :param switchinfo.models.Switch switch:
    :return: Backup file name
    """
    return settings.BACKUP_PATH + '/' + switch.name


def has_backup(switch):
    """
    Check if switch has backup
    :param switchinfo.models.Switch switch:
    :return bool:
    """
    if os.path.exists(backup_file(switch)):
        return True
    else:
        return False


def backup(switch, connection_type, username, password, enable_password=None):

    print('Backing up %s switch %s using %s' % (switch.type, switch.name, connection_type))
    local_file = backup_file(switch)

    if connection_type == 'SFTP' or connection_type == 'SCP':
        if switch.type == 'Cisco':
            remote_file = 'running-config'
        elif switch.type == 'Aruba' or switch.type == 'ProCurve':
            remote_file = '/cfg/running-config'
        elif switch.type == 'Extreme':
            remote_file = '/config/primary.cfg'
            local_file += '.xml'
        elif switch.type == 'HP':
            remote_file = 'startup.cfg'
        else:
            raise ValueError('%s backup not supported for switch type: %s' % (connection_type, switch.type))

        import paramiko
        try:
            t = paramiko.Transport((switch.ip, 22))
            t.connect(username=username, password=password)

            if connection_type == 'SFTP':
                sftp = paramiko.SFTPClient.from_transport(t)
                sftp.get(remote_file, local_file)
            elif connection_type == 'SCP':
                from scp import SCPClient
                scp = SCPClient(t)
                scp.get(remote_file, local_file)

        except paramiko.ssh_exception.SSHException as e:
            raise BackupFailed(e)
    else:  # CLI based backup
        cli = get_connection(switch.type, connection_type)()
        try:
            cli.login(switch.ip, username, password, enable_password)
        except (OSError, ConnectionError) as e:
            raise BackupFailed(e)

        if switch.type == 'Cisco':
            cli.command('copy running-config %s/%s' % (settings.BACKUP_URL, switch.name),
                        'Address or name of remote host', '?')
            cli.command('\n', 'Destination filename', '?')
            try:
                cli.command('\n', '#')
            except UnexpectedResponse as e:
                if e.payload.strip() == '':
                    from time import sleep
                    sleep(3)
                else:
                    print(ord(e.payload.strip()[0]))
                    raise e
            if os.path.exists(local_file):
                subprocess.check_output(['sed', '-i', '/ntp clock-period.*/d', local_file])
            else:
                raise BackupFailed('Switch did not upload config to %s' % local_file)

        else:
            raise ValueError('CLI based backup not supported for %s' % switch.type)
    return local_file
