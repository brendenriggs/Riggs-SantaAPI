FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

# set working directory
WORKDIR /project/app

# set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependencies
RUN apt-get update \
  && apt-get -y install netcat gcc \
  && apt-get clean

# install python dependencies
RUN pip install --upgrade pip
COPY /requirements.txt .
RUN pip install -r requirements.txt


COPY . .