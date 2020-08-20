FROM python:3.6.12-alpine3.12
MAINTAINER farktronix

RUN pip3 install influxdb

COPY crontab /etc/crontabs/root

COPY airquality.py /root/
RUN chmod +x /root/airquality.py

ENTRYPOINT ["crond", "-f", "-d", "8"]
