from .ComwareCLI import ComwareCLI


class HP1910CLI(ComwareCLI):
    def login(self, ip, username, password, enable_password=None):
        self.command('_cmdline mode on')