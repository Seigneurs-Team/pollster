FROM ubuntu:latest
FROM python:3.9-slim

SHELL ["/bin/bash", "-c"]

WORKDIR /pollster
COPY . /pollster

EXPOSE 8000
ENV PYTHONUNBUFFERED=1

RUN python3 -m venv venv && source venv/bin/activate
RUN pip3 install -r requirements.txt

CMD cd src && python3 -m app.manage runserver