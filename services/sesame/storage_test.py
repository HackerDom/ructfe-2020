import requests
import random
import string

from bs4 import BeautifulSoup

def store_secret(secret):
	url = 'http://' + host + ':4280/'
	response = requests.post(url, data = { 'secret': secret })
	soup = BeautifulSoup(response.text, features="html.parser")
	key = soup.find(id="key").text.strip()
	if len(key) != 32:
		raise Exception("Failed to store secret!")
	return key

def load_secret(key):
	url = 'http://' + host + ':4280/' + key
	response = requests.get(url)
	soup = BeautifulSoup(response.text, features="html.parser")
	secret = soup.find(id="secret").text.strip()
	if len(secret) != 31:
		raise Exception("Failed to fetch secret by key %s! Was %s." % (key, secret))
	return secret

import sys
host = sys.argv[1] if len(sys.argv) > 1 else 'localhost'

MAXITEMS = 4096
items = [(None, None)] * MAXITEMS
current_item = 0

i = 0
while True:
	secret = ''.join(random.choice(string.ascii_uppercase) for _ in range(31))
	key = store_secret(secret)
	items[current_item] = (key, secret)
	current_item = (current_item + 1) % MAXITEMS
	assert load_secret(key) == secret
	i += 1
	if i % 100 == 0:
		for k, s in items[:100]:
			if k == None:
				break
			assert load_secret(k) == s
	if i % 10 == 0:
		print('processed: %d, current: %d' % (i, current_item))

