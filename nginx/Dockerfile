FROM ubuntu:16.04

# set up usefull staff
RUN apt-get update
RUN apt-get install -y nginx

COPY default.conf /etc/nginx/sites-enabled/default

EXPOSE 80
