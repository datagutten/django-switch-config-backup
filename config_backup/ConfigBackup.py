from config_backup.models import CommonBackupOption, SwitchBackupOption
from config_backup.switch_cli.get_connection import get_connection


def backup_options(switch):
    try:
        options = CommonBackupOption.objects.get(type=switch.type)
    except CommonBackupOption.DoesNotExist:
        options = []

    try:
        switch_options = SwitchBackupOption.objects.get(switch=switch)
        if switch_options.exclude:
            print('%s excluded from backup' % switch)
            return
        if switch_options.username:
            options.username = switch_options.username
        if switch_options.password:
            options.password = switch_options.password
        if switch_options.enable_password:
            options.enable_password = switch_options.enable_password
        if switch_options.connection_type:
            options.connection_type = switch_options.connection_type
    except SwitchBackupOption.DoesNotExist:
        if not options:
            print('No options found for type %s or switch %s' % (switch.type, switch))
            return
    return options


def connect(switch, connection_type='Telnet'):
    connection = get_connection(switch.type, connection_type)()
    options = backup_options(switch)
    connection.login(switch.ip, options.username,
                     options.password, options.enable_password)
