class BackupException(Exception):
    pass


class ConnectionFailed(BackupException):
    pass


class BackupFailed(BackupException):
    """Exception raised when backup fails"""
    pass
