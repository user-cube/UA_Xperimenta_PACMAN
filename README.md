# Artificial Inteligence - Pacman
Client-Server PACMAN game using A*.

This code was developed to Xperimenta UA 2019.

## Install

* Clone this repository
* Create a virtual environment:

```console
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```
* Intall xterm:

Ubuntu based:
```shell
$ sudo apt update
$ sudo apt install xterm
```
Fedora:
```shell
$ sudo dnf update
$ sudo dnf install xterm
```

Arch based:
```shell
$ sudo pacman -S xterm
```

### How to run:
Open 2 terminals.

On the first one run:
``` shell
$ ./xperimentaServer.sh
```
Terminal 2:
```shell
$ source venv/bin/actibate
$ python3 xperimenta.py
```

## Runing into Raspberry Pi
If you are running into a Raspberry Pi you should consider use python 3.7.
<details><summary>Show me how to do it!</summary>

### Upgrading to Python 3.7.0
First install the dependencies needed to build.
```console
$ sudo apt-get update
$ sudo apt-get install -y build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev libffi-dev
```
Compile (takes a while!)
```console
$ wget https://www.python.org/ftp/python/3.7.0/Python-3.7.0.tar.xz
$ tar xf Python-3.7.0.tar.xz
$ cd Python-3.7.0
$ ./configure --prefix=/usr/local/opt/python-3.7.0
$ make -j 4
```
Install 
```console
$ sudo make altinstall
```
Make Python 3.7 the default version, make aliases.
```console
$ sudo ln -s /usr/local/opt/python-3.7.0/bin/pydoc3.7 /usr/bin/pydoc3.7
$ sudo ln -s /usr/local/opt/python-3.7.0/bin/python3.7 /usr/bin/python3.7
$ sudo ln -s /usr/local/opt/python-3.7.0/bin/python3.7m /usr/bin/python3.7m
$ sudo ln -s /usr/local/opt/python-3.7.0/bin/pyvenv-3.7 /usr/bin/pyvenv-3.7
$ sudo ln -s /usr/local/opt/python-3.7.0/bin/pip3.7 /usr/bin/pip3.7
```
Now it's time to open `.bashrc` and make aliases.
```console
$ vim ~/.bashrc
```
And add the following lines:
```bash
alias python='/usr/bin/python3.7'
alias python3='/usr/bin/python3.7'
```
Now you can delete the source folder of python.
```console
$ cd ..
$ sudo rm -r Python-3.7.0
$ rm Python-3.7.0.tar.xz
```
### Compile PyGame on Raspberry Pi
Install dependencies:
```console
$ sudo apt-get install git python3-dev python3-setuptools python3-numpy python3-opengl \
    libsdl-image1.2-dev libsdl-mixer1.2-dev libsdl-ttf2.0-dev libsmpeg-dev \
    libsdl1.2-dev libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev \
    libtiff5-dev libx11-6 libx11-dev fluid-soundfont-gm timgm6mb-soundfont \
    xfonts-base xfonts-100dpi xfonts-75dpi xfonts-cyrillic fontconfig fonts-freefont-ttf libfreetype6-dev
```
Grab source
```console 
$ wget https://github.com/pygame/pygame/archive/1.9.4.zip
$ unzip 1.9.4.zip
$ mv pygame-1.9.4/ pygame
```
Finally build and install
```console
$ cd pygame
$ python3.7 setup.py build
$ sudo python3 setup.py install
```
Now run (takes a while):
```console
$ pip install -r requirements.txt
```
</details>

## Credits
Sprites from https://github.com/rm-hull/big-bang/tree/master/examples/pacman/data
