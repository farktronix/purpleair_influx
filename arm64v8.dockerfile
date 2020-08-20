FROM arm64v8/python:3.6-alpine3.11
MAINTAINER farktronix

RUN pip3 install influxdb

COPY crontab /etc/crontabs/root

COPY airquality.py /root/
RUN chmod +x /root/airquality.py

ENTRYPOINT ["crond", "-f", "-d", "8"]
