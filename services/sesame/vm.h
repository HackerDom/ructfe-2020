#pragma once

#include "types.h"

#define OP_nop       0
#define OP_dup       1
#define OP_swap      2
#define OP_pushn     3
#define OP_pushs     4
#define OP_pusharg   5
#define OP_pop       6
#define OP_cmps      7
#define OP_brnull    8
#define OP_encode    9
#define OP_hash      10
#define OP_name      11
#define OP_store     12
#define OP_load      13
#define OP_list      14
#define OP_respond   15

void respond(int32 fd, uint64 code, const char *text, const char *content_type);
void run_handler(byte *handler, int32 fd, uint64 *params);