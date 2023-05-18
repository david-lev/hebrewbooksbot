FROM python:3.10-alpine

WORKDIR /app

COPY . .

RUN apk update && \
    apk add --no-cache sqlite && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

ENV PYTHONPATH "${PYTHONPATH}:/app"
