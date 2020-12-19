#include <sys/epoll.h>

#include "types.h"
#include "storage.h"
#include "http.h"

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
				bzero(buf, sizeof(buf));

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
