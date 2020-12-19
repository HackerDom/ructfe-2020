import sys
import htmlmin

with open('index.html', 'r') as f:
	index = f.read()
	index = htmlmin.minify(index, remove_empty_space=True)

output = [ 
	'#pragma once', 
	'#include "types.h"', 
	'', 
	'byte pg_index[] = { %s };' % ', '.join([hex(ord(c)) for c in index]) ]


for l in output:
	print(l)