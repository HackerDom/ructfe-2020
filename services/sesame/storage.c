#include <uuid/uuid.h>
#include <time.h>

#include "storage.h"

#define MAXITEMS 4096
#define MAXNODES (MAXITEMS * 32 + 1)

#define HAS_VALUE -1

typedef struct 
{
	char key[32];
	char value[32];
} slot;

typedef struct
{
	uint32 trans[26];
	int32 trans_count;
	uint32 value; 
} node;

node nodes[MAXNODES];
slot slots[MAXITEMS];
uint32 current_item;
uint32 current_node;

int32 logfd;


bool store_item_impl(slot *item);

void init_storage()
{
	current_item = 0;
	current_node = 1;
	bzero(nodes, sizeof(nodes));
	bzero(slots, sizeof(slots));
	nodes[0].trans_count = HAS_VALUE;

	if ((logfd = open("storage", O_RDWR | O_CREAT, 0666)) < 0)
	{
		perror("fuck storage\n");
		exit(1);
	}

	uint32 items_read = 0;
	slot item;
	while (true)
	{
		int32 bytesRead = read(logfd, &item, sizeof(item));

		if (!bytesRead)
			break;

		if (bytesRead < sizeof(item))
		{
			printf("Item %u is corrupt\n", items_read);
			break;
		}

		store_item_impl(&item);
		items_read++;
	}
}

uint32 allocate_node()
{
	uint32 i;
	for (i = 0; i < MAXNODES; i++)
	{
		uint32 idx = (i + current_node) % MAXNODES;
		if (nodes[idx].trans_count)
			continue;
		current_node = idx + 1;
		return idx;
	}
	printf("failed to allocate node!\n");
	exit(1);
}

void delete_item(slot *item)
{
	uint32 current = 0;
	char *key;
	uint32 path[32] = { 0 };
	uint32 i = 0;
	for (key = item->key; *key && key < item->value; key++)
	{
		uint32 n = *key - 'A';
		path[i++] = current;
		current = nodes[current].trans[n] - 1;
		if (current > MAXNODES)
			return;
	}

	bzero(&nodes[current], sizeof(node));

	for (i--; i > 0; i--)
	{
		if (nodes[current].value)
			break;

		key--;
		uint32 n = *key - 'A';
		if (nodes[current].trans_count == 0)
		{
			nodes[path[i]].trans[n] = 0;
			nodes[path[i]].trans_count--;
		}
		current = path[i];
	}
}

uint32 add_item(const slot *item)
{
	if (slots[current_item].key[0])
		delete_item(&slots[current_item]);

	slots[current_item] = *item;

	uint32 added_at = current_item;
	current_item = (current_item + 1) % MAXITEMS;

	return added_at;
}

void copy_value(const void *src, void *dest)
{
	((uint64 *)dest)[0] = ((uint64 *)src)[0];
	((uint64 *)dest)[1] = ((uint64 *)src)[1];
	((uint64 *)dest)[2] = ((uint64 *)src)[2];
	((uint64 *)dest)[3] = ((uint64 *)src)[3];
}

bool store_item_impl(slot *item)
{
	uint32 current = 0;

	uint32 new_item = add_item(item);

	char *key;
	for (key = item->key; *key && key < item->value; key++)
	{
		uint32 n = *key - 'A';
		if (n >= 26)
			return false;
		if (!nodes[current].trans[n])
		{
			uint32 nd = allocate_node();
			nodes[current].trans[n] = nd + 1;
			nodes[current].trans_count++;
		}
		current = nodes[current].trans[n] - 1;
	}

	if (nodes[current].value)
		return false;

	nodes[current].value = new_item + 1;
	nodes[current].trans_count = HAS_VALUE;

	return true;
}

char * store_item(char *key, char *value)
{
	if (!key || !value)
		return 0;
	slot item;
	copy_value(value, item.value);
	copy_value(key, item.key);

	if (store_item_impl(&item))
	{
		if (write(logfd, &item, sizeof(item)) < 0)
		{
			perror("store_item failed to write!");
			exit(1);
		}
		return key;
	}

	return 0;
}

char * load_item(const char *key, char *buffer)
{
	if (!key || !buffer)
		return 0;

	uint32 current = 0;

	while (*key)
	{
		uint32 n = *key - 'A';
		if (n >= 26)
			return 0;
		if (!nodes[current].trans[n])
			return 0;
		current = nodes[current].trans[n] - 1;
		key++;
	}

	if (!nodes[current].value)
		return 0;

	copy_value(slots[nodes[current].value - 1].value, buffer);
	buffer[32] = 0; 

	return buffer;
}

char * list_items(uint32 skip, uint32 take, char *buffer, uint64 length)
{
	if (!buffer)
		return 0;

	if (take * 33 > length)
		return 0;

	buffer[0] = 0;

	uint32 i;
	for (i = skip; i < skip + take; i++)
	{
		int64 idx = (current_item + MAXITEMS - i) % MAXITEMS;

		strncat(buffer, slots[idx].key, 32);
		strcat(buffer, "\n");
	}

	return buffer;
}

char * gen_key(char *buffer, uint64 modifier)
{
	byte binuuid[16];
	uuid_generate_random(binuuid);

	time_t now = time(0);
	struct tm *now_tm = localtime(&now);
	uint64 time_id = now_tm->tm_year + now_tm->tm_mon * 7 + 
		now_tm->tm_mday * 31 + now_tm->tm_hour * 167 + now_tm->tm_min * 401;

	uint64 multiplier = binuuid[0] + 3;
	for (int i = 0; i < 32; i++)
	{
		buffer[i] = 'A' + ((time_id * multiplier + i * 7) % 26);
		multiplier = (multiplier * 167 + modifier) % 16769023;
	}

	return buffer;
}