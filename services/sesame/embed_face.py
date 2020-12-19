import sys

with open('index.html', 'r') as f:
	html = f.read()
with open('index.min.js', 'r') as f:
	html = html % f.read()

output = [ 
	'#pragma once', 
	'#include "types.h"', 
	'', 
	'byte face[] = { %s };' % ', '.join([hex(ord(c)) for c in html]) ]


for l in output:
	print(l)