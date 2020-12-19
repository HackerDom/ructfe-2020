#include "types.h"
#include "epoll.h"
#include "num.h"
#include "vm.h"
#include "storage.h"
#include "baz.vm.h"
#include "face.html.h"

#include <asm/errno.h>

#define PORT 4280u

int64 parse_int(const char *str)
{
	const int64 base = 10;

	if (!str)
		return 0;

	int64 result = 0;
	while (*str)
	{
		result = result * base + (*str - '0');
		str++;
	}

	return result;
}

uint64 parse_int_hex(const char *str)
{
	const uint64 base = 16;

	uint64 result = 0;
	while (*str)
	{
		result = result * base + (*str < 'a' ? *str - '0' : *str - 'a' + 10);
		str++;
	}

	return result;
}

bool to_string(int64 value, char *buffer, int64 buffer_length)
{
	const int64 base = 10;

	if (value < 0 && buffer_length > 0)
	{
		*buffer = '-';
		return to_string(-value, buffer + 1, buffer_length - 1);
	}

	int64 i;
	for (i = 0; i < buffer_length - 1; i++)
	{
		buffer[i] = (value % base) + '0';
		value /= base;
		if (!value)
		{
			buffer[i + 1] = 0;
			break;
		}
	}

	if (i == buffer_length - 1)
		return false;

	char *end = buffer + i;
	while (end > buffer)
	{
		char temp = *buffer;
		*buffer = *end;
		*end = temp;
		end--;
		buffer++;
	}

	return true;
}

bool to_string_hex(uint64 value, char *buffer, int64 buffer_length)
{
	const uint64 base = 16;

	int64 i;
	for (i = 0; i < buffer_length - 1; i++)
	{
		buffer[i] = "0123456789abcdef"[value % base];
		value /= base;
		if (!value)
		{
			buffer[i + 1] = 0;
			break;
		}
	}

	if (i == buffer_length - 1)
		return false;

	char *end = buffer + i;
	while (end > buffer)
	{
		char temp = *buffer;
		*buffer = *end;
		*end = temp;
		end--;
		buffer++;
	}

	return true;
}

uint64 strcmp(const char *str1, const char *str2)
{
	if (!str1 || !str2)
		return !str1 && !str2;
	while (*str1 && (*str1 == *str2))
	{
		str1++;
		str2++;
	}
	return *str1 - *str2;
}

void strcat(char *str1, const char *str2)
{
	while (*str1)
		str1++;
	while (*str2)
	{
		*str1 = *str2;
		str1++;
		str2++;
	}
	*str1 = 0;
}

void strncat(char *str1, const char *str2, uint64 n)
{
	while (*str1)
		str1++;
	while (*str2 && n)
	{
		*str1 = *str2;
		str1++;
		str2++;
		n--;
	}
	*str1 = 0;
}

void memzero(void *data, int64 length)
{
	int64 *ptr = (int64 *)data;
	int64 i;
	for (i = 0; i < length / sizeof(int64); i++)
	{
		*ptr = 0L;
		ptr++;
	}
	byte *ptr2 = (byte *)ptr;
	for (i = 0; i < length % sizeof(int64); i++)
	{
		*ptr2 = 0;
		ptr2++;
	}
}

void print(const char *message)
{
	if (!message)
	{
		print("(null)");
		return;
	}
	write(1, message, strlen(message));
}

void nprint(int64 n)
{
	char buf[32];
	to_string(n, buf, sizeof(buf));
	print(buf);
}

void hprint(uint64 n)
{
	char buf[32];
	to_string_hex(n, buf, sizeof(buf));
	print(buf);
}

int32 socket();

int32 reuseaddr(int32 fd);

int32 bind(int32 fd, struct sockaddr *addr, int32 addr_len);

void listen(int32 fd, int32 queue);

int32 accept(int32 fd, struct sockaddr *addr, int32 *addr_len);

void close(int32 fd);

uint32 fcntl(int32 fd, int32 cmd, uint32 arg);

int32 epoll_create1(int32 flags);

int32 epoll_ctl(int32 __epfd, int32 __op, int32 __fd, struct epoll_event *__event);

int32 epoll_wait(int32 __epfd, struct epoll_event *__events, int32 __maxevents, int32 __timeout);

int32 create_listener()
{
	int32 sock = socket();
	if (sock < 0)
	{
		print("fuck socket\n");
		exit(1);
	}

	if (reuseaddr(sock) < 0)
    {
		print("fuck reuseaddr\n");
		exit(1);
	}

	struct sockaddr name;

	name.sin_family = 2;
	name.sin_port = (uint16)(((PORT & 0xff) << 8) | (PORT >> 8));
	name.sin_addr.s_addr = INADDR_ANY;

	if (bind(sock, &name, sizeof(name)))
	{
		print("fuck bind\n");
		exit(1);
	}

	return sock;
}

void make_nonblocking(int32 sfd)
{
	uint32 flags = fcntl(sfd, F_GETFL, 0);

	if (flags < 0)
	{
		print("fuck fcntl\n");
		exit(1);
	}

	flags |= O_NONBLOCK;
	if (fcntl(sfd, F_SETFL, flags) < 0)
	{
		print("fuck fcntl\n");
		exit(1);
	}
}

#define MAXEVENTS 64

#define ST_HANDLER 0 
#define ST_KEY 1
#define ST_VALUE 2

void process_request(int32 fd, char *request)
{
	char buf[1024];
	int64 i = -1;
	uint64 state = ST_HANDLER;

	byte *handler = handler_badrequest;
	uint64 params[2] = { 0 };

	//print(request);

	while (*request)
	{
		if (i >= (int64)sizeof(buf))
		{
			handler = handler_badrequest;
			break;
		}
		char c = *request;
		if (c == '\n')
			break;
		if (i >= 0)
		{
			if ((c < 'a' || c > 'z') && (c < 'A' || c > 'Z') && (c < '0' || c > '9') && c != ',')
			{
				buf[i] = 0;
				if (i > 0)
				{
					i = 0;
					if (state == ST_HANDLER)
					{
						state = ST_KEY;

						if (!strcmp(buf, "mix"))
							handler = handler_mix;
						else if (!strcmp(buf, "mixnew"))
							handler = handler_mixnew;
						else if (!strcmp(buf, "memorize"))
							handler = handler_memorize;
						else if (!strcmp(buf, "list"))
							handler = handler_list;
						else
						{
							respond(fd, 200, face, "text/html");
							return;
						}
					}
					else if (state == ST_KEY)
					{
						state = ST_VALUE;

						if (handler == handler_mix)
						{
							if (!strcmp(buf, "name"))
								params[0] = (uint64)(request + 1);
						}
						else if (handler == handler_mixnew)
						{
							if (!strcmp(buf, "what"))
								params[0] = (uint64)(request + 1);

						}
						else if (handler == handler_memorize)
						{
							if (!strcmp(buf, "name"))
								params[0] = (uint64)(request + 1);
							if (!strcmp(buf, "what"))
								params[1] = (uint64)(request + 1);
						}
						else if (handler == handler_list)
						{
							if (!strcmp(buf, "skip"))
								params[0] = (uint64)(request + 1);
							if (!strcmp(buf, "take"))
								params[1] = (uint64)(request + 1);
						}
					}
					else
					{
						state = ST_KEY;

						*request = 0;
					}
				}
			}
			else
				buf[i++] = c;
		}
		else if (*request == '/')
			i = 0;

		request++;
	}

	if (handler == handler_list)
	{
		params[0] = parse_int((const char *)params[0]);
		params[1] = parse_int((const char *)params[1]);
	}

	run_handler(handler, fd, params);
}

void main()
{
	struct epoll_event event;
	struct epoll_event events[MAXEVENTS];

	memzero(&event, sizeof(event));
	memzero(events, sizeof(events));

	int32 listener = create_listener();

	make_nonblocking(listener);

	listen(listener, 100);

	int32 efd = epoll_create1(0);
	if (efd < 0)
	{
		print("fuck epoll\n");
		exit(1);
	}

	event.data.fd = listener;
	event.events = EPOLLIN | EPOLLET;
	if (epoll_ctl(efd, EPOLL_CTL_ADD, listener, &event) < 0)
	{
		print("fuck epoll_ctl\n");
		exit(1);
	}

	while (true)
	{
		int32 n = epoll_wait(efd, events, MAXEVENTS, -1);

		int32 i;
		for (i = 0; i < n; i++)
		{
			if ((events[i].events & EPOLLERR) ||
				(events[i].events & EPOLLHUP) ||
				(!(events[i].events & EPOLLIN)))
			{
				print("epoll error\n");
				close (events[i].data.fd);
				continue;
			}
			else if (listener == events[i].data.fd)
			{
				while (true)
				{
					struct sockaddr in_addr;
					int32 in_len = sizeof(in_addr);
					
					int32 cli = accept(listener, &in_addr, &in_len);
					if (cli < 0)
					{
						if ((cli == -EAGAIN) ||
							(cli == -EWOULDBLOCK))
						{
							break;
						}
						else
						{
							print("accept error\n");
							break;
						}
					}
 
					make_nonblocking(cli);

					memzero(&event, sizeof(event));
					event.data.fd = cli;
					event.events = EPOLLIN | EPOLLET;
					if (epoll_ctl(efd, EPOLL_CTL_ADD, cli, &event) < 0)
					{
						print("fuck epoll_ctl\n");
						exit(1);
					}
				}
			}
			else
			{
				int64 count;
				char buf[1024];

				count = read(events[i].data.fd, buf, sizeof(buf));

				if (count > 0)
					process_request(events[i].data.fd, buf);

				close(events[i].data.fd);
			}
		}
	}


	close(listener);
}

void _start()
{
	init_storage();

	main();

	exit(0);
}

void test_math()
{
	char buf[256];
	read(0, buf, sizeof(buf));

	uint192 a;
	uint64 b;
	char m = buf[0];

	uint64 args[4];

	uint64 i, j;
	for (i = 1; i < sizeof(buf); i++)
	{
		if (buf[i] == ';')
			buf[i] = 0;
	}
	for (i = 1, j = 0; i < sizeof(buf), j < 4; i++)
	{
		if (!buf[i])
		{
			args[j] = parse_int_hex(&buf[i + 1]);
			j++;
		}
	}
	a.i0 = args[0];
	a.i1 = args[1];
	a.i2 = args[2];
	b = args[3];

	uint32 r;
	if (m == '+')
	{
		a = add(a, b);
		hprint(a.i0);print(";");hprint(a.i1);print(";");hprint(a.i2);print("\n");
	}
	else if (m == '*')
	{
		a = multiply(a, b);
		hprint(a.i0);print(";");hprint(a.i1);print(";");hprint(a.i2);print("\n");
	}
	else if (m == '/')
	{
		a = divmod(a, b, &r);
		hprint(a.i0);print(";");hprint(a.i1);print(";");hprint(a.i2);print(";");hprint(r);print("\n");
	}
}