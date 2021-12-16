import time
from abc import ABC


class Connection(ABC):
    connection: object
    connection_type: str
    timeout: int = 5

    def connect(self, ip, username=None, password=None):
        raise NotImplementedError

    def set_timeout(self, timeout: int):
        self.timeout = timeout

    def command(self, cmd: bytes, read_until: bytes = None,
                timeout: int = 2) -> bytes:
        raise NotImplementedError

    def read(self) -> bytes:
        raise NotImplementedError

    def read_until(self, match: bytes) -> bytes:
        response = b''
        while response.find(match) == -1:
            response += self.read()

        return response

    def read_wait(self):
        count = 1
        found = False
        response = b''
        while count < self.timeout:
            response += self.read()
            if response != b'':
                found = True
            if response == b'' and found:
                break

            print('Wait %d' % count)
            time.sleep(1)
            count += 1
        return response
