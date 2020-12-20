import random
import string

# def add_to_tree(tree, key, stats):
# 	node = tree
# 	for c in key:
# 		if not c in node:
# 			node[c] = {}
# 			stats['nodes'] += 1
# 		node = node[c]
# 	if not 'has_value' in node:
# 		node['has_value'] = True
# 		stats['values'] += 1

# tree = {}

KEYLEN = 32
MAXVALUES = 4096
MAXNODES = MAXVALUES * KEYLEN + 1

def create_node():
	return {
		'trans': {},
		'has_value': False
	}

def delete_from_tree(tree, key, stats):
	nodes, values = tree['nodes'], tree['values']
	track = []
	node = nodes[0]
	for c in key:
		track.append((node, c))
		node = nodes[node['trans'][c]]
	node['has_value'] = False
	stats['values'] -= 1
	values.remove(key)
	for n, c in reversed(track):
		if len(node['trans']) == 0:
			stats['nodes'] -= 1
			del n['trans'][c]
		node = n
	#print('deleted!', stats, nodes)


def add_to_tree(tree, key, stats):
	nodes, values = tree['nodes'], tree['values']
	if len(values) == MAXVALUES:
		delete_from_tree(tree, next(iter(values)), stats)
	node = nodes[0]
	for c in key:
		if not c in node['trans']:
			for z in range(len(nodes)):
				i = (z + tree['free_node']) % len(nodes)
				if len(nodes[i]['trans']) == 0 and i != 0 and not nodes[i]['has_value']:
					node['trans'][c] = i
					stats['nodes'] += 1
					tree['free_node'] = (i + 1) % len(nodes)
					break
			if not c in node['trans']:
				raise Exception('We fucked up!')
		node = nodes[node['trans'][c]]
	if not node['has_value']:
		node['has_value'] = True
		stats['values'] += 1
		values.add(key)

tree = {
	'nodes': [create_node() for _ in range(MAXNODES)],
	'values': set(),
	'free_node': 1
}

stats = { 'nodes': 0, 'values': 0 }

while True:
	for i in range(100):
		key = ''.join(random.choice(string.ascii_uppercase) for _ in range(KEYLEN))
		add_to_tree(tree, key, stats)
	#print(tree)
	print(stats)
	print('nodes to values ratio: %.2f' % (stats['nodes'] / stats['values']))
	input()