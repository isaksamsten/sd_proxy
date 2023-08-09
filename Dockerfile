FROM ubuntu:22.04

ENV HOSTNAME=""
ENV PORT="8888"
ENV USERNAME=""
ENV PASSWORD_HASH=""
ENV XMLTV="xmltv.xml"

RUN apt update && \
    apt install -y python3 python3-pip

WORKDIR /usr/src/
COPY . .
RUN ls -lA
RUN pip install pip -U && pip install .
RUN pip freeze

CMD ["sh", "-c", "python3 -m sd_proxy --username=${USERNAME} --password-hash=${PASSWORD_HASH} --port=${PORT} --hostname=${HOSTNAME} --xmltv=${XMLTV}"]



