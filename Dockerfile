FROM python:3.10-alpine

# set work directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBUG 0

# install psycopg2
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev \
    && apk add libffi-dev libressl-dev \
    && apk add --no-cache jpeg-dev zlib-dev libjpeg \
    && apk add rust cargo
# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g' /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

COPY . .

# add and run as non-root user
RUN adduser -D myuser
RUN chmod -R 777 /app
USER myuser
ENTRYPOINT ["/app/entrypoint.sh"]