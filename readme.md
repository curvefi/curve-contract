# curve-xdai

> documentation for curve-xdai deployment

0. setup python3

```
sudo wget https://www.python.org/ftp/python/3.7.3/Python-3.7.3.tar.xz
sudo tar xf Python-3.7.3.tar.xz 
 cd ./Python-3.7.3 && /
 sudo ./configure && /
 sudo make && /
 sudo make install && /
 sudo update-alternatives --install /usr/bin/python python /usr/local/bin/python3.7 10
```

1. brownie & ganache 
```
python3 -m pip install --user pipx
python3 -m pipx ensurepath
source ~/.bashrc
pipx install eth-brownie
npm install -g ganache-cli
```

2. curve
```
cd .. && git clone https://github.com/curvefi/curve-contract.git && cd curve-contract
python3 -m venv venv
pip install -r requirements.txt
```

