#include "http.h"
#include "resources.h"
#include "storage.h"

void respond_bytes(char *response, uint64 *response_length, uint64 code, const char *text, uint64 length, const char *content_type)
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

	uint64 pos = sprintf(response, 
		"%s\r\n"
		"Server: sesame\r\n"
		"Content-Length: %llu\r\n"
		"Content-Type: %s\r\n"
		"Connection: close\r\n\r\n", 
		code_msg, length, content_type);
	if (text)
		memcpy(response + pos, text, length);
	*response_length = pos + length;
}

void respond(char *response, uint64 *response_length, uint64 code, const char *text, const char *content_type)
{
	respond_bytes(response, response_length, code, text, text ? strlen(text) : 0, content_type);
}

void redirect(char *response, uint64 *response_length, const char *location)
{
	*response_length = sprintf(response, 
		"HTTP/1.1 303 See Other\r\n"
		"Location: /%s\r\n"
		"Connection: close\r\n\r\n", location);
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

bool read_request(char **request, struct strbuf *verb, struct strbuf *url)
{
	struct strbuf *output = verb;
	char *rp;
	for (rp = *request; *rp; rp++)
	{
		char c = *rp;
		if (c == ' ')
		{
			if (output == verb)
				output = url;
			else
				break;
		}
		else if (c == '/')
			continue;
		else if (c < 'A' || c > 'Z')
			break;
		else if (!try_add_char(output, c))
			return false;
	}
	for (; *rp; rp++)
	{
		if (*rp == '\n')
		{
			*request = rp + 1;
			return true;
		}
	}
	return false;
}

bool read_headers(char **request, struct strbuf *cl)
{
	char *cl_start = strstr(*request, "Content-Length");
	if (!cl_start)
		return false;

	char *rp;
	for (rp = cl_start; *rp; rp++)
	{
		char c = *rp;
		if (c == '\n')
			break;
		else if (c < '0' || c > '9')
			continue;
		else if (!try_add_char(cl, c))
			break;
	}
	char * headers_end = strstr(rp, "\r\n\r\n");
	if (!headers_end)
		return false;

	*request = headers_end + 4;
	return true;
}

bool read_body(char *request, uint64 content_length, struct strbuf *secret)
{
	char *cl_start = strstr(request, "secret");
	if (!cl_start)
		return false;

	char *rp;
	for (rp = cl_start; rp < request + content_length; rp++)
	{
		char c = *rp;
		if ((c < 'A' || c > 'Z') && (c < '0' || c > '9'))
			continue;
		else if (!try_add_char(secret, c))
			break;
	}

	return true;
}

bool try_send_resource(const char *name, char *response, uint64 *response_length)
{
	if (!strcmp("A", name))
	{
		respond_bytes(response, response_length, 200, res_bg, size_bg, "image/png");
		return true;
	}
	return false;
}

bool process_request(char *request, char *response, uint64 *response_length)
{
	// printf("Request:\n%s\n", request);

	struct strbuf verb, url, cl, secret;
	init_strbuf(&verb, 4);
	init_strbuf(&url, 32);
	init_strbuf(&cl, 8);
	init_strbuf(&secret, 32);

	if (!read_request(&request, &verb, &url))
		return false;

	char page[MAXSEND];
	bzero(page, sizeof(page));

	// printf("Verb: %s\nUrl: %s\n\n", verb.data, url.data);

	if (!strcmp("GET", verb.data))
	{
		if (try_send_resource(url.data, response, response_length))
			return true;
		char * value = 0;
		if (url.length == 32)
		{
			value = load_item(url.data, secret.data);
			if (!value)
				value = "";
		}
		render_page(page, url.data, value);
		respond(response, response_length, 200, page, "text/html");
		return true;
	}
	
	if (!strcmp("POST", verb.data))
	{
		if (!read_headers(&request, &cl))
			return false;
		if (cl.length != 0)
		{
			uint64 content_length = atoll(cl.data);
			if (strlen(request) < content_length)
				return false;
			read_body(request, content_length, &secret);
		}
		if (secret.length == 0)
		{
			respond(response, response_length, 400, 0, "text/html");
			return true;
		}

		char value[32];
		char key[64];
		bzero(key, sizeof(key));

		for (int i = 0; i < 64; i++)
		{	
			gen_key(key, i);

			if (load_item(key, value))
				continue;

			store_item(key, secret.data);
			break;
		}

		render_page(page, key, secret.data);
		redirect(response, response_length, key);
		return true;
	}

	respond(response, response_length, 400, 0, "text/html");
	return true;
}