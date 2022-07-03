import switchinfo.load_info.load_interfaces
from django.core.management.base import CommandError
from switchinfo.management.commands import SwitchBaseCommand
from switchinfo.models import Vlan

from config_backup.ConfigBackup import connect_cli
from config_backup.switch_cli.connections.exceptions import CLIException


class Command(SwitchBaseCommand):
    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument('--interface', nargs='?', type=str)
        parser.add_argument('--untagged', nargs='?', type=int)
        parser.add_argument('--uplink', nargs='?', type=int)

    def handle(self, *args, **cmd_options):
        if cmd_options['uplink']:
            vlan_id = cmd_options['uplink']
            mode = 'uplink'
        elif cmd_options['untagged']:
            vlan_id = cmd_options['untagged']
            mode = 'untagged'
        else:
            raise CommandError('Invalid argument combination')

        vlan_obj = Vlan.objects.get(vlan=vlan_id)
        switches = self.handle_arguments(cmd_options)
        if mode == 'untagged' and len(switches) > 1:
            raise CommandError('Untagged interfaces can only be changed at one switch at the time')

        for switch in switches:
            print(switch)
            try:
                cli = connect_cli(switch)
            except CLIException as e:
                print(e)
                continue

            if vlan_obj not in switch.vlan.all():
                print('vlan %s is not on switch %s' % (vlan_obj, switch))
                cli.vlan_name(vlan_obj.vlan, vlan_obj.name)

            for interface in switch.neighbor_interfaces():
                print('%d tagged vlans on %s' % (interface.tagged_vlans.count(), interface))
                if vlan_obj not in interface.tagged_vlans.all() and interface.tagged_vlans.count() > 0:
                    print('Add vlan %s to interface %s' % (vlan_obj, interface))
                    cli.tagged_vlan(interface.interface, vlan_obj.vlan)
                else:
                    print('Vlan %s is already tagged on interface %s' % (vlan_obj, interface))

            if mode == 'untagged':
                interface_obj = switch.interfaces.get(interface=cmd_options['interface'])
                print(cli.untagged_vlan(interface_obj.interface, vlan_obj.vlan).encode())

            cli.save()

            switchinfo.load_info.load_interfaces(switch)
            switchinfo.load_info.load_vlan(switch)
