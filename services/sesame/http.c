#include "http.h"
#include "face.html.h"
#include "storage.h"

void respond(int32 fd, uint64 code, const char *text, const char *content_type)
{
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

	char response[1024];
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

void redirect(int32 fd, const char *location)
{
	char response[256];
	sprintf(response, 
		"HTTP/1.1 303 See Other\r\n"
		"Location: /%s\r\n"
		"Connection: close\r\n\r\n", location);

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

void render_page(char * buffer, const char * key, const char * secret)
{
	sprintf(buffer, pg_index, key, secret ? secret : "");
}

#define ST_VERB 0
#define ST_URL 1
#define ST_SECRET 2
#define ST_DONE 3

void process_request(int32 fd, char *request)
{
	printf("Request:\n%s\n", request);

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
		respond(fd, 400, 0, "text/html");
		return;
	}

	char *secret_start = strstr(request, "secret");
	if (secret_start)
	{
		for (char *rp = secret_start; *rp; rp++)
		{
			char c = *rp;
			if ((c < 'A' || c > 'Z') && (c < '0' || c > '9'))
				continue;
			else if (!try_add_char(&bufs[state], c))
				break;
		}
	}

	printf("Verb: %s\nUrl: %s\nSecret: %s\n\n", 
		bufs[ST_VERB].data, bufs[ST_URL].data, bufs[ST_SECRET].data);

	char page[1024];
	bzero(page, sizeof(page));

	if (!strcmp("GET", bufs[ST_VERB].data))
	{
		char * secret = 0;
		if (bufs[ST_URL].length == 32)
		{
			secret = load_item(bufs[ST_URL].data, bufs[ST_SECRET].data);
			if (!secret)
				secret = "";
		}
		render_page(page, bufs[ST_URL].data, secret);
		respond(fd, 200, page, "text/html");
		return;
	}
	
	if (!strcmp("POST", bufs[ST_VERB].data))
	{
		char key[64];
		bzero(key, sizeof(key));
		gen_key(key);
		printf("saving by key: %s\n", key);

		store_item(key, bufs[ST_SECRET].data);
		render_page(page, key, bufs[ST_SECRET].data);
		redirect(fd, key);
		return;
	}

	respond(fd, 400, 0, "text/html");
}