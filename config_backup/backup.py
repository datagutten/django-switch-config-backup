import os
import subprocess

from django.conf import settings
from switchinfo.models import Switch

from .ConfigBackup import connect_cli, connect_http
from .exceptions import BackupFailed
from .switch_cli.connections.exceptions import UnexpectedResponse

try:
    local_path = settings.BACKUP_PATH
except AttributeError:
    local_path = None


def backup_file(switch):
    """
    Get backup file name with path
    :param switchinfo.models.Switch switch:
    :return: Backup file name
    """
    if local_path:
        return local_path + '/' + switch.name


def has_backup(switch: Switch):
    """
    Check if switch has backup
    :param switchinfo.models.Switch switch:
    :return bool:
    """
    if local_path and os.path.exists(backup_file(switch)):
        return True
    else:
        return False


def remote_file_name(switch_type):
    if switch_type in ['Cisco', 'Cisco IOS XE']:
        return 'running-config'
    elif switch_type == 'Aruba' or switch_type == 'ProCurve':
        return '/cfg/running-config'
    elif switch_type == 'Extreme':
        return '/config/primary.cfg'
    elif switch_type == 'HP':
        return 'startup.cfg'
    elif switch_type == '3Com':
        return '3comoscfg.cfg'
    elif switch_type == 'Fortinet':
        return 'sys_config'
    else:
        raise BackupFailed(
            'File backup not supported for switch type: %s' % switch_type)


def backup(switch, connection_type, username, password, enable_password=None):
    print('Backing up %s switch %s using %s' % (switch.type, switch.name, connection_type))
    local_file = backup_file(switch)
    if connection_type not in ['SCP', 'SFTP', 'Telnet', 'SSH', 'http']:
        raise BackupFailed('Invalid connection type: %s' % connection_type)

    if connection_type == 'SFTP' or connection_type == 'SCP':
        import paramiko
        remote_file = remote_file_name(switch.type)

        try:
            try:
                t = paramiko.Transport((switch.ip, 22))
                t.connect(username=username, password=password)
            except paramiko.ssh_exception.AuthenticationException as e:
                t = paramiko.Transport((switch.ip, 22))
                t.connect(username=username, password=enable_password)

            if connection_type == 'SFTP':
                sftp = paramiko.SFTPClient.from_transport(t)
                sftp.get(remote_file, local_file)
            elif connection_type == 'SCP':
                from scp import SCPClient
                scp = SCPClient(t)
                scp.get(remote_file, local_file)

            if not os.path.exists(local_file):
                raise BackupFailed('Switch did not upload config to %s' % local_file)

        except Exception as e:
            if str(e) == '':
                raise BackupFailed(str(type(e)))
            else:
                raise BackupFailed(e)
    elif connection_type == 'http':
        http = connect_http(switch)
        config = http.config()
        with open(local_file, 'wb') as fp:
            fp.write(config)

    else:  # CLI based backup
        try:
            cli = connect_cli(switch)
        except UnexpectedResponse as e:
            print(e, e.payload.decode('utf-8'))
            raise e

        try:
            if not hasattr(settings, 'BACKUP_URL'):
                raise NotImplementedError('Setting BACKUP_URL is not set')
            url = '%s/%s' % (settings.BACKUP_URL, switch.name)
            print(cli.backup_copy(url))

            if not os.path.exists(local_file):
                raise BackupFailed('Switch did not upload config to %s' % local_file)
        except NotImplementedError:
            try:
                config = cli.backup()
                with open(local_file, 'wb') as fp:
                    fp.write(config)
            except NotImplementedError:
                raise BackupFailed('CLI based backup not supported for %s' % switch.type)

    if switch.type == 'Cisco':
        subprocess.run(['sed', '-i', '/ntp clock-period.*/d', local_file])
    return local_file
