import sys

with open('index.html', 'r') as f:
	index = f.read()
with open('form.html', 'r') as f:
	form = f.read()

output = [ 
	'#pragma once', 
	'#include "types.h"', 
	'', 
	'byte pg_index[] = { %s };' % ', '.join([hex(ord(c)) for c in index]),
	'byte pg_form[] = { %s };' % ', '.join([hex(ord(c)) for c in form]) ]


for l in output:
	print(l)