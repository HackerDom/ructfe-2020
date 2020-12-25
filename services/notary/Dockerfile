FROM python:3.8-slim

RUN useradd -M -s /bin/false notary

RUN mkdir -p /var/notary/

WORKDIR /var/notary/

COPY notaryserver/requirements.txt .

RUN pip install -r requirements.txt

COPY notaryserver/ .

COPY entrypoint.sh .

RUN chmod +x entrypoint.sh

USER notary

ENTRYPOINT ./entrypoint.sh
