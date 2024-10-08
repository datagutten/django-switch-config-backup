from switchinfo.models import Switch

from config_backup.exceptions import BackupFailed
from config_backup.models import CommonBackupOption, SwitchBackupOption
from config_backup.switch_cli.connections.common import SwitchCli
from config_backup.switch_cli.connections.exceptions import CLIConnectionError, UnexpectedResponse
from config_backup.switch_cli.get_connection import get_cli, get_http


def backup_options(switch):
    try:
        options = CommonBackupOption.objects.get(type=switch.type)
        common = True
    except CommonBackupOption.DoesNotExist:
        options = CommonBackupOption()
        common = False

    try:
        switch_options = SwitchBackupOption.objects.get(switch=switch)
        if switch_options.exclude:
            raise BackupFailed('%s is excluded from backup' % switch)
        if switch_options.username:
            options.username = switch_options.username
        if switch_options.password:
            options.password = switch_options.password
        if switch_options.enable_password:
            options.enable_password = switch_options.enable_password
        if switch_options.connection_type:
            options.connection_type = switch_options.connection_type
    except SwitchBackupOption.DoesNotExist:
        if not common:
            raise BackupFailed('No options found for type %s or switch %s' % (switch.type, switch))
    return options


def connect(switch: Switch, connection_type=None):
    options = backup_options(switch)
    if not connection_type:
        cli = get_cli(switch.type)(options.connection_type)
    else:
        cli = get_cli(switch.type)(connection_type)

    cli.login(switch.ip, options.username, options.password, options.enable_password)
    return cli


def connect_cli(switch: Switch) -> 'SwitchCli':
    options = backup_options(switch)
    cli = get_cli(switch.type)('ssh')
    try:
        cli.login(switch.ip, options.username, options.password, options.enable_password)
    except (ConnectionError, AttributeError, CLIConnectionError, UnexpectedResponse) as e:
        if cli.connection_type == 'ssh':
            print('SSH login failed, trying telnet')
            cli = get_cli(switch.type)('telnet')
            cli.login(switch.ip, options.username, options.password, options.enable_password)
        else:
            raise e
    return cli


def connect_http(switch: Switch):
    options = backup_options(switch)
    if options is None:
        print('No backup options found for switch %s' % switch)
        return
    http = get_http(switch.type)(switch.ip)
    http.login(options.username, options.password)
    return http
