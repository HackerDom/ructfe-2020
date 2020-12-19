#pragma once

#include "types.h"

void init_storage();
char * store_item(char *key, char *value);
char * load_item(const char *key, char *buffer);
char * list_items(uint64 skip, uint64 take, char *buffer, uint64 length);

char * gen_key(char *buffer, uint64 modifier);