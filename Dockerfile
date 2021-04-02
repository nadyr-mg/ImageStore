FROM python:3.8-alpine

WORKDIR /usr/src/app

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev jpeg-dev zlib-dev

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY ./entrypoint.sh .
RUN ["chmod", "+x", "/usr/src/app/entrypoint.sh"]

COPY . .

ENTRYPOINT ["sh", "/usr/src/app/entrypoint.sh"]