FROM python:3

ENV PYTHONUNBUFFERED 1

WORKDIR /app

ADD . /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --upgrade pip setuptools wheel

RUN pip install -r /app/requirements.txt

COPY . /app
