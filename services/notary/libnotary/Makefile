CC=gcc
CFLAGS=-Wall -shared -fvisibility=hidden
CSTRIP=-s
SECFLAGS=-fPIC -Wl,-z,relro,-z,now -Wl,-z,noexecstack -fstack-protector-strong

SOURCES=src/curve.c src/point.c


.PHONY: all clean


all:
	$(CC) $(CFLAGS) $(SECFLAGS) $(SOURCES) $(CSTRIP) -o libnotary.so

clean:
	rm -f libnotary.so
