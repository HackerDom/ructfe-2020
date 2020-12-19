import sys

opcodes = {
	'nop':      0,
	'dup':      1,
	'swap':     2,
	'pushn':    3,
	'pushs':    4,
	'pusharg':  5,
	'pop':      6,
	'cmps':     7,
	'brnull':   8,
	'encode':   9,
	'hash':     10,
	'name':     11,
	'store':    12,
	'load':     13,
	'list':     14,
	'respond':  15,
}

def compile_handler(lines, output):
	h, name = lines[0].split()
	if h != 'handler':
		raise Exception('First line is "%s" instead of a header definition' % lines[0])
	lines = lines[1:]

	labels = {}
	i = 0
	for l in lines:
		if l[0] == ':':
			if l in labels:
				raise Exception('Label "%s" already defined' % l)
			labels[l] = i
			continue
		if 'pushn' in l:
			i += 4
		elif 'pushs' in l or 'cmps' in l:
			i += 2 + len(l.split(maxsplit=1)[1])
		elif 'pusharg' in l or 'brnull' in l:
			i += 1
		i += 1

	ops = []

	for l in lines:
		if l[0] == ':':
			continue

		op, *args = l.split(maxsplit=1)
		if not op in opcodes:
			raise Exception('Invalid operation "%s"' % op)
		ops.append(opcodes[op])

		if op == 'pushn':
			assert len(args) == 1
			n = int(args[0])
			ops += [ n & 0xff, (n >> 8) & 0xff, (n >> 16) & 0xff, (n >> 24) & 0xff ]
		elif op == 'pusharg':
			assert len(args) == 1
			n = int(args[0])
			ops.append(n)
		elif op == 'pushs' or op == 'cmps':
			assert len(args) == 1
			assert len(args[0]) < 256
			ops.append(len(args[0]))
			ops += [ord(c) for c in args[0]]
			ops.append(0)
		elif op == 'brnull':
			assert len(args) == 1
			assert args[0] in labels
			ops.append(labels[args[0]])

	output.append('byte handler_%s[] = { %s };' % (name, ', '.join([hex(e) for e in ops])))


lines = [e.strip() for e in sys.stdin.readlines() if e.strip() != '']

handlers = []

handler = []
for l in lines:
	if l == '---':
		handlers.append(handler)
		handler = []
	else:
		handler.append(l)

output = [ '#pragma once', '#include "types.h"', '' ]
for h in handlers:
	compile_handler(h, output)

for l in output:
	print(l)