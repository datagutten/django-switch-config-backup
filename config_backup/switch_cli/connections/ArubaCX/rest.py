import requests


class ArubaRest:
    def __init__(self, ip, verify_ssl=False):
        self.session = requests.Session()
        self.session.verify = verify_ssl
        self.url = 'https://%s/rest/v1/' % ip

    # def _get(self, uri):

    def login(self, username, password):
        response = self.session.post(self.url + 'login', {
            'username': username,
            'password': password
        })
        response.raise_for_status()

    def config_json(self, name='running-config') -> str:
        response = self.session.get(self.url + 'fullconfigs/%s' % name)
        return response.text

    def config(self, name='running-config') -> bytes:
        response = self.session.get(self.url + 'configs/%s' % name,
                                    headers={'Accept': 'text/plain'})
        return response.content

    def interfaces(self) -> dict:
        response = self.session.get('system/interfaces')
        return response.json()
