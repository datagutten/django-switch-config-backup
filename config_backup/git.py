import os
import subprocess


class Git:
    repo_path = None

    def __init__(self, repo_path):
        self.repo_path = repo_path
        if not os.path.exists(repo_path):
            raise FileNotFoundError('Repository path "%s" not found' % repo_path)

    def add(self, file):
        if os.path.exists(file):
            cmd = ['git',
                   '--git-dir', self.repo_path + '/.git',
                   '--work-tree', self.repo_path,
                   'add', file,
                   ]
            return subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        else:
            raise FileNotFoundError('File not found: ' + file)

    def diff(self, file):
        if os.path.exists(file):
            cmd = ['git',
                   '--git-dir', self.repo_path + '/.git',
                   '--work-tree', self.repo_path,
                   'diff', file,
                   ]
            return subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        else:
            raise FileNotFoundError('File not found: ' + file)

    def commit(self, message):
        try:
            return subprocess.check_output(['git',
                                            '--git-dir', self.repo_path + '/.git',
                                            '--work-tree', self.repo_path,
                                            'commit',
                                            '-m', message],
                                           universal_newlines=True,
                                           stderr=subprocess.STDOUT)

        except subprocess.CalledProcessError as e:
            if not e.returncode == 1:
                raise e
