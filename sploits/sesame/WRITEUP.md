SESAME is a service for storing secrets. It supports two operations:
1. Store a new secret and give you the access code.
2. Take an access code and give you the secret back.

## Vuln 1

Codes are generated using `uuid_generate_random()`. But if we look closely...

Only the first byte of the uuid is actually used, plus some function of current time (with minute precision). 
This is the only input for the code generation. With some math on top it's used to get all 32 letters of the code.

This means that every minute only 256 different codes are generated! Let's just replicate the algorithm and brute-force the one random byte.

Sploit: [hack_1.py](hack_1.py)

#### How to fix

Make any change to the key generation algorithm; should be enough to just patch one of the constants.

## Vuln 2

Let's take a look at that `epoll` server. For each client connection it keeps a state object that consists of receive buffer, send buffer, 
transferred bytes counter and send buffer length. These objects are tied to file descriptors, so if a client comes with the same fd it'll get the same state object. 

When a new client is connected, the corresponding state is cleared: byte counter, buffer length are set to 0. But the buffers themselves are not zeroed out. 
So maybe if we get assigned a state that was used to request a flag, we can make the same request handled again! The only catch here is that after reading a bunch of bytes from a client socket the code sets the following byte in the buffer to 0.

Descriptors are assigned sequentially, so if we connect at the time when no one else is there, we have a good chance of getting the same fd the checksystem just used.

Now, what will we send? We need to somehow skip the zero byte, and all the http parsing code stops reading upon finding a zero.  
Let's take a close look at the function parsing Content-Length. It runs `start = strstr(request, "Content-Length")` first, and then starts parsing the number from `start + strlen("Content-Length:")`. All we need to do now is to put our zero precisely in place of the colon, and it'll get ignored!

Sploit: [hack_2.py](hack_2.py)

#### How to fix

- Patch the literal `Content-Length:` to `Content-Length`.
OR
- Put up a proxy that filters malfored http requests.

## Vuln 3

... was not planned. But who knows, maybe you've found one? After all, this service involves a self-made http server in C.
