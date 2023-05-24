from . import connections

cli_classes = {
    'Cisco': connections.Cisco.CiscoCLI,
    'Comware': connections.Comware.ComwareCLI,
    '3Com': connections.Comware.ComwareCLI,
    'HP': connections.Comware.ComwareCLI,
    'ProCurve': connections.HP.ProCurveCLI,
    'Aruba': connections.HP.ProCurveCLI,
}

http_classes = {
    'Aruba CX': connections.ArubaCX.ArubaRest,
    'Aruba CX REST API': connections.ArubaCX.ArubaRest,
}


def get_cli(switch_type):
    if switch_type in cli_classes:
        return cli_classes[switch_type]
    else:
        raise AttributeError('CLI not supported for %s' % switch_type)


def get_http(switch_type):
    if switch_type in http_classes:
        return http_classes[switch_type]
    else:
        raise AttributeError('http(s) not supported for %s' % switch_type)
