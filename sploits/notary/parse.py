#!/usr/bin/env python3

from bs4 import BeautifulSoup


class Parser:
    def __init__(self, page):
        self.soup = BeautifulSoup(page, features='lxml')

    def csrf_token(self):
        return self.soup.find('input', dict(name='csrf_token'))['value']

    def profile_field(self, label, code_wrapped=False):
        selector = f'div:has(>strong:-soup-contains("{label}"))'
        if code_wrapped:
            return self.soup.select_one(selector + '>code').text
        return self.soup.select_one(selector).contents[-1][2:].strip()

    def public_key(self):
        return self.profile_field('Public key', code_wrapped=True)

    def phone(self):
        return self.profile_field('Phone')

    def address(self):
        return self.profile_field('Address')

    def username(self):
        suffix = '\'s profile'
        header = self.soup.select_one(f'h2:-soup-contains("{suffix}")').text.strip()
        return header.split(suffix)[0]

    def author_url(self, soup=None):
        if soup is None:
            soup = self.soup
        return soup.select_one(':-soup-contains("Signed by")>a[href^="/user/"]')['href']

    def document_text(self, soup=None):
        if soup is None:
            soup = self.soup
        return soup.select_one('.card-body>p').text.strip()

    def document_urls(self, soup=None):
        if soup is None:
            soup = self.soup
        links = soup.select('a[href^="/doc/"]')
        return [link['href'] for link in links]

    def document_cards(self):
        for card in self.soup.select('.row .card:has(a[href^="/doc/"])'):
            document_url = self.document_urls(soup=card)[0]
            text = self.document_text(soup=card)
            user_url = self.author_url(soup=card)
            yield document_url, text, user_url
