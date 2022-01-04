from . import connections

cli_classes = {
    'Cisco': connections.Cisco.CiscoCLI,
    'Comware': connections.Comware.ComwareCLI,
    '3Com': connections.Comware.ComwareCLI,
    'HP': connections.Comware.ComwareCLI,
    'ProCurve': connections.HP.ProCurveCLI,
    'Aruba': connections.HP.ProCurveCLI,
}


def get_cli(switch_type):
    if switch_type in cli_classes:
        return cli_classes[switch_type]
    else:
        raise AttributeError('CLI not supported for %s' % switch_type)
