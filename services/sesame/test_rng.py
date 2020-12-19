import datetime
import uuid

def time_id():
	now = datetime.datetime.now()
	return now.year + now.month * 7 + now.day * 31 + now.hour * 167 + now.minute * 401

def gen_key(modifier):
	u = uuid.uuid4()

	key = [0] * 32
	multiplier = int(u.bytes[0])
	for i in range(32):
		key[i] = (time_id() * multiplier) % 26
		multiplier = (multiplier * 167 + modifier) % 16769023
	return ''.join(chr(ord('A') + e) for e in key)

total = 0
collisions = 0
used = set()
while True:
	for i in range(10):
		key = gen_key(i)
		if not key in used:
			break
	total += 1
	if key in used:
		collisions += 1
	else:
		used.add(key)
	if total % 256 == 0:
		print('Total %d, collision rate = %.2f' % (total, collisions / total))
		total = 0
		collisions = 0
		input()