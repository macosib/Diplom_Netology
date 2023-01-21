# syntax=docker/dockerfile:1
FROM python:3

WORKDIR /usr/src/core

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir --upgrade -r requirements.txt

EXPOSE 8000

COPY . .