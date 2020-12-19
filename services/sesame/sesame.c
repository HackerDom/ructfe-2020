#include <sys/epoll.h>

#include "types.h"
#include "storage.h"
#include "face.html.h"

#define PORT 4280u

int32 create_listener()
{
	int32 sock = socket(AF_INET, SOCK_STREAM, 0);
	if (sock < 0)
	{
		perror("fuck socket\n");
		exit(1);
	}

	int enable = 1;
	if (setsockopt(sock, SOL_SOCKET, SO_REUSEADDR, &enable, sizeof(int)) < 0)
    {
		perror("fuck reuseaddr\n");
		exit(1);
	}

	struct sockaddr_in name;
	bzero(&name, sizeof(name));
	name.sin_family = AF_INET;
	name.sin_addr.s_addr = INADDR_ANY;
	name.sin_port = htons(PORT);

	if (bind(sock, (struct sockaddr *)&name, sizeof(name)))
	{
		perror("fuck bind\n");
		exit(1);
	}

	return sock;
}

void make_nonblocking(int32 sfd)
{
	uint32 flags = fcntl(sfd, F_GETFL, 0);

	if (flags < 0)
	{
		perror("fuck fcntl\n");
		exit(1);
	}

	flags |= O_NONBLOCK;
	if (fcntl(sfd, F_SETFL, flags) < 0)
	{
		perror("fuck fcntl\n");
		exit(1);
	}
}

#define MAXEVENTS 64

void respond(int32 fd, uint64 code, const char *text, const char *content_type)
{
	char response[40960];
	response[0] = 0;

	char * code_msg;
	switch (code)
	{
		case 200:
			code_msg = "HTTP/1.1 200 OK";
			break;
		case 400:
			code_msg = "HTTP/1.1 400 Bad Request";
			break;
		case 404:
			code_msg = "HTTP/1.1 404 Not Found";
			break;
		default:
			code_msg = "HTTP/1.1 500 Internal Server Error";
			break;
	}

	sprintf(response, 
		"%s\r\n"
		"Server: sesame\r\n"
		"Content-Length: %lu\r\n"
		"Content-Type: %s\r\n"
		"Connection: close\r\n\r\n"
		"%s", code_msg, text ? strlen(text) : 0, content_type, text ? text : "");

	if (write(fd, response, strlen(response)) < 0)
		printf("failed to write response!\n");
}

struct strbuf
{
	size_t length;
	size_t limit;
	char data[64];
};

void init_strbuf(struct strbuf * buf, size_t limit)
{
	bzero(buf, sizeof(*buf));
	if (limit >= sizeof(buf->data))
		limit = sizeof(buf->data) - 1;
	buf->limit = limit;
}

bool try_add_char(struct strbuf * buf, char c)
{
	if (buf->length < buf->limit)
	{
		buf->data[buf->length++] = c;
		return true;
	}
	return false;
}

#define ST_VERB 0
#define ST_URL 1
#define ST_SECRET 2
#define ST_DONE 3

void process_request(int32 fd, char *request)
{
	// printf("Request:\n%s\n", request);

	// parse verb
	// parse url
	// if GET: if url len < 32: face; otherwise face % flag form
	// if POST: if url len < 32: 400; otherwise save flag, face % flag form

	int state = ST_VERB;
	struct strbuf bufs[3];
	init_strbuf(&bufs[ST_VERB], 4);
	init_strbuf(&bufs[ST_URL], 32);
	init_strbuf(&bufs[ST_SECRET], 32);

	for (char *rp = request; *rp && state < ST_SECRET; rp++)
	{
		char c = *rp;
		if (c == ' ')
			state++;
		else if (c == '/')
			continue;
		else if (c < 'A' || c > 'Z')
			break;
		else if (!try_add_char(&bufs[state], c))
			break;
	}

	if (state != ST_SECRET)
	{
		respond(fd, 400, face, "text/html");
		return;
	}

	char *secret_start = strstr(request, "secret");
	if (secret_start)
	{
		for (char *rp = secret_start; *rp; rp++)
		{
			char c = *rp;
			if (c < 'A' || c > 'Z')
				continue;
			else if (!try_add_char(&bufs[state], c))
				break;
		}
	}

	printf("Verb: %s\nUrl: %s\nSecret: %s\n", 
		bufs[ST_VERB].data, bufs[ST_URL].data, bufs[ST_SECRET].data);

	respond(fd, 200, face, "text/html");
}

void run()
{
	struct epoll_event event;
	struct epoll_event events[MAXEVENTS];

	bzero(&event, sizeof(event));
	bzero(events, sizeof(events));

	int32 listener = create_listener();

	make_nonblocking(listener);

	listen(listener, 100);

	int32 efd = epoll_create1(0);
	if (efd < 0)
	{
		perror("fuck epoll\n");
		exit(1);
	}

	event.data.fd = listener;
	event.events = EPOLLIN;
	if (epoll_ctl(efd, EPOLL_CTL_ADD, listener, &event) < 0)
	{
		perror("fuck epoll_ctl\n");
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
				printf("epoll error\n");
				close(events[i].data.fd);
				continue;
			}
			else if (listener == events[i].data.fd)
			{
				while (true)
				{
					struct sockaddr_in in_addr;
					int32 in_len = sizeof(in_addr);
					bzero(&in_addr, in_len);
					
					int32 cli = accept(listener, (struct sockaddr *)&in_addr, &in_len);
					if (cli < 0)
					{
						if ((errno == EAGAIN) || (errno == EWOULDBLOCK))
						{
							break;
						}
						else
						{
							printf("accept error: %d\n", errno);
							break;
						}
					}
 
					make_nonblocking(cli);

					bzero(&event, sizeof(event));
					event.data.fd = cli;
					event.events = EPOLLIN;
					if (epoll_ctl(efd, EPOLL_CTL_ADD, cli, &event) < 0)
					{
						perror("fuck epoll_ctl\n");
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

int main()
{
	init_storage();

	run();

	return 0;
}
