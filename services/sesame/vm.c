#include "vm.h"
#include "types.h"
#include "storage.h"

void respond(int32 fd, uint64 code, const char *text, const char *content_type)
{
	char buf[32];
	to_string(text ? strlen(text) : 0, buf, sizeof(buf));

	char response[40960];
	response[0] = 0;
	switch (code)
	{
		case 200:
			strcat(response, "HTTP/1.1 200 OK\r\n");
			break;
		case 201:
			strcat(response, "HTTP/1.1 201 Created\r\n");
			break;
		case 400:
			strcat(response, "HTTP/1.1 400 Bad Request\r\n");
			break;
		case 404:
			strcat(response, "HTTP/1.1 404 Not Found\r\n");
			break;
		case 409:
			strcat(response, "HTTP/1.1 409 Conflict\r\n");
			break;
		default:
			strcat(response, "HTTP/1.1 500 Internal Server Error\r\n");
			break;
	}
	strcat(response, "Server: baz\r\n");
	strcat(response, "Content-Length: ");strcat(response, buf);strcat(response, "\r\n");
	strcat(response, "Content-Type: ");strcat(response, content_type);strcat(response, "\r\n");
	strcat(response, "Connection: close\r\n\r\n");
	if (text)
		strcat(response, text);

	write(fd, response, strlen(response));
}

void run_handler(byte *handler, int32 fd, uint64 *params)
{
	uint64 stack[32];
	uint64 sp = 0;
	uint64 ip = 0;

	char flagbuffer[64];
	char hashbuffer[64];
	char namebuffer[64];
	char listbuffer[1024];

	uint64 t;
	while (true)
	{
		byte opcode = handler[ip];
		ip++;

		//print("opcode: ");nprint(opcode);print("\n");

		switch (opcode)
		{
			case OP_nop:
				break;
			case OP_dup:
				stack[sp] = stack[sp - 1];
				sp++;
				break;
			case OP_swap:
				t = stack[sp - 1];
				stack[sp - 1] = stack[sp - 2];
				stack[sp - 2] = t;
				break;
			case OP_pushn:
				stack[sp] = *(uint32 *)&handler[ip];
				sp++;
				ip += sizeof(uint32);
				break;
			case OP_pushs:
				stack[sp] = (uint64)&handler[ip + 1];
				sp++;
				ip += handler[ip] + 2;
				break;
			case OP_pusharg:
				stack[sp] = params[handler[ip]];
				sp++;
				ip++;
				break;
			case OP_pop:
				sp--;
				break;
			case OP_cmps:
				t = (uint64)&handler[ip + 1];
				if (!strcmp((const char *)t, (const char *)stack[sp - 1]))
				{
					stack[sp] = (uint64)&handler[ip + 1];
					sp++;
				}
				else
				{
					stack[sp] = 0;
					sp++;
				}
				ip += handler[ip] + 2;
				break;
			case OP_brnull:
				if (!stack[sp - 1])
				{
					ip = handler[ip];
				}
				else
					ip++;
				break;
			case OP_encode:
				stack[sp - 1] = (uint64)encode_flag((const char *)stack[sp - 1], flagbuffer);
				break;
			case OP_hash:
				stack[sp - 1] = (uint64)hash_flag((const char *)stack[sp - 1], hashbuffer);
				break;
			case OP_name:
				stack[sp - 1] = (uint64)name_flag((const char *)stack[sp - 1], namebuffer);
				break;
			case OP_store:
				t = (uint64)store_item((char *)stack[sp - 1], (char *)stack[sp - 2]);
				sp--;
				stack[sp - 1] = t;
				break;
			case OP_load:
				stack[sp - 1] = (uint64)load_item((const char *)stack[sp - 1], flagbuffer);
				break;
			case OP_list:
				stack[sp - 2] = (uint64)list_items(stack[sp - 1], stack[sp - 2], listbuffer, sizeof(listbuffer));
				sp--;
				break;
			case OP_respond:
				respond(fd, stack[sp - 1], (const char *)stack[sp - 2], "text/plain");
				return;
		}
	}
}