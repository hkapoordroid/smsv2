FROM ubuntu:16.04
 
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN mkdir -p /usr/src/app/logs
 
RUN apt-get update -y
RUN apt-get install -y python-pip
RUN apt-get install -y gunicorn

COPY requirements.txt /usr/src/app/

RUN pip install -r requirements.txt

COPY . /usr/src/app

EXPOSE 9000

#RUN gunicorn -c gunicorn.conf.py wsgi:application

ENTRYPOINT ["/usr/local/bin/gunicorn", "--config", "/usr/src/app/gunicorn.conf.py", "wsgi:application"]