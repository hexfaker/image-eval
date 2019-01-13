FROM ubuntu:18.04

COPY requirements.txt /app/requirements.txt
WORKDIR /app

RUN apt-get update && \
    apt-get install -y \
    python3 \
    python3-pip \
    uwsgi \
    uwsgi-plugin-python3 # && \
    rm -rf /var/lib/{apt,dpkg,cache,log}

RUN pip3 --no-cache-dir install -r requirements.txt
RUN mkdir -p /data/media && chown -R www-data:www-data /data
COPY ./ /app/

ENV DEBUG=false VAR_DIR=/data/
RUN make static
USER www-data:www-data
ENTRYPOINT uwsgi --ini config/image-eval.ini


