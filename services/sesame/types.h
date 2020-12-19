#pragma once

typedef int int32;
typedef long long int64;
typedef unsigned int uint32;
typedef unsigned long long uint64;
typedef __uint128_t uint128;
typedef unsigned char byte;
typedef int64 intptr;
typedef int64 bool;
typedef unsigned short uint16;
typedef intptr string;

#define false 0
#define true 1

/* Internet address.  */
typedef uint32 in_addr_t;
struct in_addr
{
	in_addr_t s_addr;
};

/* Structure describing an Internet socket address.  */
struct sockaddr
{
	uint16 sin_family;
	uint16 sin_port;			/* Port number.  */
	struct in_addr sin_addr;		/* Internet address.  */

	/* Pad to size of `struct sockaddr'.  */
	unsigned char sin_zero[16 -
		sizeof(uint16) -
		sizeof(uint16) -
		sizeof(struct in_addr)];
};

#define	INADDR_ANY		((uint32) 0x00000000)

#define O_NONBLOCK   04000
#define F_GETFL   3 /* Get file status flags.  */
#define F_SETFL   4 /* Set file status flags.  */

#define printn(p1) print(p1);print("\n");
#define printn3(p1,p2,p3) print(p1);nprint(p2);print(p3);print("\n");

typedef struct {
	uint64 i2, i1, i0;
} uint192;


void print(const char *message);
void nprint(int64 num);

int64 write(int32 fd, const void *data, int64 length);
int64 read(int32 fd, void *data, int64 length);

uint64 strlen(const char *str);
uint64 strcmp(const char *str1, const char *str2);
void strcat(char *str1, const char *str2);
void strncat(char *str1, const char *str2, uint64 n);
bool to_string(int64 value, char *buffer, int64 buffer_length);

void memzero(void *data, int64 length);

bool to_string_hex(uint64 value, char *buffer, int64 buffer_length);

int32 openrw(const char *path);
__attribute__((noreturn)) void exit(int32 code);