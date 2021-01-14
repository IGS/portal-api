# To use this for local development:
# First build the image:
#
#   $ docker build -t portal-api:latest .
#

FROM ubuntu:16.04

MAINTAINER IGS IFX <igs-ifx@som.umaryland.edu>

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    apache2 libapache2-mod-wsgi \
    python2.7 python-pip python-setuptools python-dev build-essential \
    curl screen

# curl --tlsv1 -vk https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN mkdir /export 

WORKDIR /export/portal-api

RUN pip install --upgrade pip==10.0.1 

RUN pip install -Iv Flask==0.12.2 \
    && pip install -Iv Flask-Cors==3.0.3 \
    && pip install -Iv Flask-GraphQL==1.4.1 \
    && pip install -Iv graphene==1.3 \
    && pip install -Iv graphql-core==1.1 \
    && pip install -Iv py2neo==3.1.2 \ 
    && pip install -Iv requests==2.12.4 \
    && pip install -Iv ujson==1.35 \
    && pip install -Iv mysql-connector==2.2.9 \
    && pip install -Iv boto3==1.11.9 \
    && pip install -Iv pyyaml==5.3 \
    && pip install -Iv Flask-Caching==1.8.0 \
    && pip install -Iv pyzmq==19.0.2


# CMD ["python", "app.py"]
COPY ./portal-apache2.conf /etc/apache2/sites-available/portal-apache2.conf

RUN a2enmod proxy
RUN a2enmod proxy_http

RUN a2dissite 000-default.conf
RUN a2ensite portal-apache2.conf

EXPOSE 80

CMD /usr/sbin/apache2ctl -D FOREGROUND
