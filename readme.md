# curve-deploy
Docker container for deploying and hacking on [curve.fi](curve.fi) DAO and contracts

<br>

##  ✅ Prerequisites
[docker](https://docs.docker.com/get-docker/) 

<br>

##  🏁 Quick Start

First pull the docker image

```
docker pull pythonpete32/curve-deploy:latest
```

Find the `IMAGE ID` by running 

```
docker images
```

then run launch a docker container with an interactive terminal

```
docker run -it <IMAGE_ID> /bin/bash
```

<br>

##  💻 Development console

```
. ./venv/bin/activate          
pip install -r requirements.txt
brownie console
```

##   Deploy Curve DAO

soon™



If you have questions or need help please drop into the Aragon [Discord](https://discord.com/invite/remTh8w) support channel!