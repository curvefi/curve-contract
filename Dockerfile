FROM ubuntu:20.04

############################# install dependencies #############################


RUN apt-get update && apt-get upgrade -y && \
    apt-get install apt-utils -y \
    sudo \ 
    build-essential \
    git \
    curl \
    wget \
    python \
    vim 


############################# Setup non-root user #############################


RUN useradd -ms /bin/bash hacker && \
    usermod -aG sudo hacker && \
    echo "hacker ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

USER hacker

WORKDIR /home/hacker

ENV NPM_CONFIG_PREFIX=/home/hacker/.npm-global

ENV PATH=$PATH:/home/hacker/.npm-global/bin:/home/hacker/.local/bin

COPY . .


################################## Setup Node ##################################


RUN curl -sL https://deb.nodesource.com/setup_12.x | sudo -E bash - && \
    sudo apt-get install -y nodejs && \
    npm i -g ganache-cli


########################### Setup Python Environment ###########################


RUN sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv && \
    python3 -m pip install --user pipx && \ 
    python3 -m pipx ensurepath && \
    pipx install eth-brownie


################################# Setup Aragon #################################


RUN npm i -g @aragon/cli 

RUN ( echo "y" && cat) | aragon ipfs install

RUN ipfs init
    
RUN python3 -m venv venv


################################## Setup Curve ##################################


# RUN . ./venv/bin/activate           # <-- CALL INSIDE CONTAINER
# RUN pip install -r requirements.txt # <-- CALL INSIDE CONTAINER

CMD [ "bash" ] 

