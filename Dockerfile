FROM alpine:3.7 as base

FROM base as builder

RUN mkdir /install
WORKDIR /install

COPY requirements.txt /requirements.txt
RUN apk add --no-cache py2-pip \
    && pip install --install-option="--prefix=/install" -r /requirements.txt

FROM base
COPY --from=builder /install /usr
RUN apk add --no-cache ca-certificates uwsgi-python uwsgi-http

RUN adduser -D -g '' app
USER app
COPY . /home/app
WORKDIR /home/app

ENV FLASK_APP=autoapp.py LC_ALL=C.UTF-8 LANG=C.UTF-8
EXPOSE 5000

CMD [ "/usr/sbin/uwsgi", "--plugin-dir", "/usr/lib/uwsgi", \
               "--plugins", "http,python", \
               "--http", ":5000", \
               "--harakiri", "30", \
               "--idle", "false", \
               "--processes", "4", \
               "--threads", "1", \
               "--thunder-lock", \
               "--disable-logging", \
               "--reload-mercy", "20", \
               "--max-requests", "100", \
               "--die-on-term", \
               "--wsgi", "autoapp:app" ]
