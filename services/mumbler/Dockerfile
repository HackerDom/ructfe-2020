FROM gbrowdy/python-2.7.6

COPY requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt

COPY . /app
WORKDIR /app

RUN adduser --system --home /app --shell /usr/sbin/nologin --no-create-home --disabled-password -u 10000 mumbler

CMD ["start.sh"]