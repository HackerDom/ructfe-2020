FROM python:3.8

WORKDIR /services/mudarabah

COPY requirements.txt ./
RUN pip install -r requirements.txt
RUN pip list

COPY service/ .

CMD [ "gunicorn", "--bind", "0.0.0.0:3113", "--worker-class", "gevent", "--worker-connections", "1024", "main:app"]