FROM python:3.9-alpine

RUN apk update && apk upgrade
RUN apk add --no-cache python3-dev \
                        gcc \
                        libc-dev && rm -rf /var/cache/apk/*

COPY . .

RUN rm .env
RUN pip install -r requirements.txt

CMD python3 main.py
