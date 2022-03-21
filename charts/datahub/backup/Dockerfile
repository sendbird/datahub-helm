FROM ubuntu:20.04
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

USER root
RUN apt update && apt install -y mysql-client awscli

WORKDIR /home/root
