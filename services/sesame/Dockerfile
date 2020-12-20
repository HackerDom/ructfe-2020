FROM ubuntu:18.04

RUN set -eux; \
	groupadd -r sesame --gid=999; \
	useradd -r -g sesame --uid=999 --home-dir=/app --shell=/bin/bash sesame;

COPY sesame /app/sesame
COPY data /app/data

RUN chown -R sesame:sesame /app

USER sesame
WORKDIR /app

CMD ["/app/sesame"]