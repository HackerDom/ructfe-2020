
flag_alpha = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

spirits = [
"Ale",
"Porter",
"Stout",
"Lager",
"Cider",
"Mead",
"Wine",
"Port",
"Sherry",
"Vermouth",
"Vinsanto",
"Sangria",
"Champagne",
"Sake",
"Brandy",
"Cognac",
"Armagnac",
"Schnapps",
"Gin",
"Horilka",
"Metaxa",
"Rakia",
"Rum",
"Shochu",
"Soju",
"Tequila",
"Vodka",
"Bourbon",
"Whiskey",
"Absinthe",
"Juice",
"Cola",
"Water"
]

def parse_flag(flag):
	return [flag_alpha.index(c) for c in flag[:-1]]

def unparse_flag(l):
	l = ([0] * (31 - len(l))) + l
	return ''.join([flag_alpha[c] for c in l]) + '='

def parse_recipe(recipe):
	l = [spirits.index(c) for c in recipe]
	return ([0] * (len(spirits) - len(l))) + l

def unparse_recipe(l):
	return [spirits[c] for c in l]

def convert_base(x, base_from, base_to):
	n = 0
	for digit in x:
		n *= base_from
		n += digit

	n ^=      0xb0b8badbeefba115defec87edfece5f100deda11dead
	n = (n & ~0xffffffffffffffffffffffffffffffffffffffffffff) | (~n & 0xffffffffffffffffffffffffffffffffffffffffffff)
	#print(n)
	#n = ~n & 0xfffffffffffffffffffffffffffffffffffffffffffffff

	l = []
	while n > 0:
		n, value = divmod(n, base_to)
		l.append(value)
	l.reverse()

	return l

def xor_flag(x, base, y):
	n = 0
	for digit in x:
		n *= base
		n += digit

	n ^= y

	l = []
	while n > 0:
		n, value = divmod(n, base)
		l.append(value)
	l.reverse()

	return l



def flag_to_recipe(flag):
	return unparse_recipe(convert_base(parse_flag(flag), len(flag_alpha), len(spirits)))

def recipe_to_flag(recipe):
	return unparse_flag(convert_base(parse_recipe(recipe), len(spirits), len(flag_alpha)))

def int_to_flag(n):
	l = []
	while (n > 0):
		l.append(n % len(flag_alpha))
		n //= len(flag_alpha)
	l.reverse()
	l = ([0] * (31 - len(l))) + l
	return unparse_flag(l)

import random

avg_len = 0

xxx = parse_flag('Z000000000000000000000000000000=')

#print(recipe_to_flag(['Gin',]))
#exit()

for i in range(100000):
	#flag = int_to_flag(62 ** 31 - i - 1)

	#flag = int_to_flag(i)
	flag = ''.join([random.choice(flag_alpha) for _ in range(31)]) + '='

	print('%s -> %s -> %s' % (flag, ','.join(flag_to_recipe(flag)), recipe_to_flag(flag_to_recipe(flag))))
	input()

	try:
		recipe = flag_to_recipe(flag)
		avg_len += len(recipe)
		assert(recipe_to_flag(recipe) == flag)
	except:
		print('%s -> %s -> %s' % (flag, ','.join(flag_to_recipe(flag)), recipe_to_flag(flag_to_recipe(flag))))
		input()
	print(i)

print(avg_len / 100000)