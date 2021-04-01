FROM python:3.8-alpine

WORKDIR /usr/src/app

# install psycopg2 dependencies
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY ./entrypoint.sh .

COPY . .

CMD ["/usr/src/app/entrypoint.sh"]