FROM python:3.8-slim

RUN useradd -M -s /bin/false cleaner

RUN mkdir -p /var/cleaner/

WORKDIR /var/cleaner/

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY clean_db.py .

ENTRYPOINT python3 -u clean_db.py
