FROM ubuntu:22.04

ENV HOSTNAME=""
ENV PORT="8888"
ENV USERNAME=""
ENV PASSWORD_HASH=""
ENV XMLTV="/config/xmltv.xml"
ENV CACHE="/config/cache"
ENV MAX_CACHE_AGE="4320"

COPY . /tmp/src
RUN apt update && \
    apt install -y python3 python3-pip

RUN pip install pip -U && pip install /tmp/src/

WORKDIR /app

CMD ["sh", "-c", "python3 -m sd_proxy --username=${USERNAME} --password-hash=${PASSWORD_HASH} --port=${PORT} --hostname=${HOSTNAME} --xmltv=${XMLTV} --cache=${CACHE} --max-cache-age=${MAX_CACHE_AGE}"]



