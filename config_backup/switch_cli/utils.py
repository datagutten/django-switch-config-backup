import re


def strip_output(output):
    return re.sub(r'\x1B\[[A-Z0-9\?]+.+;[0-9]+H', '', output).strip()
