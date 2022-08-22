FROM python:3.10
WORKDIR /usr/src/job_website
COPY ./app ./app
COPY .env  .env
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt