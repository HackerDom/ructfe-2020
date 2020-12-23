CC=gcc
CFLAGS=-Wall -shared
SECFLAGS=-fPIC -Wl,-z,relro,-z,now -Wl,-z,noexecstack -fstack-protector-strong

SOURCES=src/curve.c src/point.c src/private.c src/public.c src/sign.c src/serialization.c


.PHONY: all clean


all:
	$(CC) $(CFLAGS) $(SECFLAGS) $(SOURCES) -o libnotary.so

clean:
	rm -f libnotary.so
