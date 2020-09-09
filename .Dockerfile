FROM ubuntu20.04

RUN apt-get update && apt-get upgrade -y

RUN useradd -ms /bin/bash hacker && \
    usermod -aG sudo hacker && \
    echo "hacker ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

USER hacker

WORKDIR /home/hacker

COPY . .

#####
