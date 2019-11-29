from .cisco_telnet import CiscoTelnet


def get_connection(switch_type, connection_type):
    if connection_type == 'Telnet':
        if switch_type == 'Cisco':
            return CiscoTelnet
        else:
            raise AttributeError('Telnet connection not supported for %s' % switch_type)
    elif connection_type == 'SSH':
        raise AttributeError('SSH connection not supported')

