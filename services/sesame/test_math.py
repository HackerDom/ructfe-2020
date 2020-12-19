
from subprocess import Popen, PIPE
import random

def pack_cmd(op, a, b):
	return '%s;%x;%x;%x;%x;' % (op, (a >> 128) & 0xffffffffffffffff, (a >> 64) & 0xffffffffffffffff, (a) & 0xffffffffffffffff, b)

def unpack_result(s):
	d0, d1, d2, r = s.split(';')
	d = (int(d0, 16) << 128) | (int(d1, 16) << 64) | (int(d2, 16));
	return (d, int(r, 16))

while True:
	a = random.randint(0, 36 ** 31)
	b = random.randint(0, 2 ** 32)

	result, rem = divmod(a, b)

	cmd = pack_cmd('/', a, b)

	print(cmd)
	p = Popen('./baz', stdin=PIPE, stdout=PIPE)
	stdout, stderr = p.communicate(cmd.encode('utf-8'))

	print(stdout)
	print(pack_cmd('=', result, rem))

	assert result == unpack_result(stdout.decode('utf-8'))[0]
	assert rem == unpack_result(stdout.decode('utf-8'))[1]


	#input()
