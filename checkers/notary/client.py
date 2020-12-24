import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass


PORT = 17171


@dataclass
class Urls:
    login: str = 'login'
    signup: str = 'signup'
    profile: str = 'profile'
    feed: str = ''
    doc: str = 'doc/{id}'
    sign: str = 'sign'
    verify: str = 'verify'

    def __init__(self, hostname):
        base = f'http://{hostname}:{PORT}/'
        for key, field in type(self).__dataclass_fields__.items():
            value = base + field.default
            setattr(self, key, value)


class Client:
    def __init__(self, hostname):
        self.urls = Urls(hostname)
        self.sess = requests.Session()

    def _extract_password(self, content):
        soup = BeautifulSoup(content, features='html.parser')
        return soup.select_one('div.alert:-soup-contains("password")>strong').text

    def _extract_token(self, content):
        soup = BeautifulSoup(content, features='html.parser')
        return soup.find('input', dict(name='csrf_token'))['value']

    def _load_token(self, url):
        resp = self.sess.get(url)
        resp.raise_for_status()
        return self._extract_token(resp.content)

    def _send_form(self, url, data):
        token = self._load_token(url)
        resp = self.sess.post(url, data=dict(csrf_token=token, **data))
        resp.raise_for_status()
        return resp

    def _load_page(self, url):
        resp = self.sess.get(url)
        resp.raise_for_status()
        return resp

    def register(self, username, name, phone, address):
        resp = self._send_form(self.urls.signup, data=dict(
            username=username, name=name, phone=phone, address=address))
        return self._extract_password(resp.content)

    def log_in(self, username, password):
        self._send_form(self.urls.login, data=dict(username=username, password=password))

    def profile(self):
        return self._load_page(self.urls.profile).content

    def feed(self):
        return self._load_page(self.urls.feed).content

    def doc(self, doc_id):
        return self._load_page(self.urls.doc.format(id=doc_id)).content

    def sign(self, title, text):
        resp = self._send_form(self.urls.sign, data=dict(title=title, text=text))
        return int(resp.url.rsplit('/', 1)[-1])

    def verify(self, title, text, signature, pubkey):
        resp = self._send_form(self.urls.verify, data=dict(
            title=title, text=text, signature=signature, pubkey=pubkey))
        return 'The signature is valid' in resp
