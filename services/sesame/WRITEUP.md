SESAME is a service for storing secrets. It supports two operations:
1. Store a new secret and give you the access code.
2. Take an access code and give you the secret back.

## Vuln 1

Codes are generated using `uuid_generate_random()`. But if we look closely...

Only the first byte of the uuid is actually used, plus some function of current time (with minute precision). 
This is the only input for the code generation. With some math on top it's used to get all 32 letters of the code.

This means that every minute only 256 different codes are generated! Let's just replicate the algorithm and brute-force the one random byte.  
This is done in [hack_1.py](hack_1.py)

## Vuln 2

Let's take a look at that `epoll` server. For each client connection it keeps a state object that consists of receive buffer, send buffer, 
transferred bytes counter and send buffer length. These objects are tied to file descriptors, so if a client comes with the same FD it'll get the same state object.  

When a new client is connected, the corresponding state is cleared: byte counter, buffer length are set to 0. But the buffers themselves are not zeroed out. 
So if we just get assigned a state that was used to request a flag, we can make the same request handled again!  

We'll create a lot of connections to get a good chance of being reassigned a state that the checksystem client used to get a flag, then send some bytes to all
connections to trigger the response. If we're lucky, we'll get a flag or two.  

The only catch here is not to spoil the original request with the bytes we send, so we have to send a prefix of that request, for instance the string 'GET'. 
Sploit: [hack_2.py](hack_2.py)

## Vuln 3

... was not planned. But who knows, maybe you've found one? After all, this service involves a self-made http server in C.
