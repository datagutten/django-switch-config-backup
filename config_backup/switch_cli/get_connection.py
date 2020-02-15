from .connections.Cisco.ssh import CiscoSSH
from .connections.Cisco.telnet import CiscoTelnet
from .connections.HP.telnet import HPTelnet
from .connections.HP.ssh import HpSSH


def get_connection(switch_type, connection_type):
    if connection_type == 'Telnet':
        if switch_type == 'Cisco':
            return CiscoTelnet
        elif switch_type == 'HP' or switch_type == 'ProCurve':
            return HPTelnet
        else:
            raise AttributeError('Telnet connection not supported for %s' % switch_type)
    elif connection_type == 'SSH':
        if switch_type == 'HP' or switch_type == 'ProCurve' or switch_type == 'Aruba':
            return HpSSH
        elif switch_type == 'Cisco':
            return CiscoSSH
        else:
            raise AttributeError('SSH connection not supported for %s' % switch_type)
    else:
        raise AttributeError('Invalid connection type')

