# CaraCara
A new Webinterface for Minecraft Servers.

## Prerequisites

```
sudo apt update
sudo apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev wget python-setuptools python-dev ncurses-dev
```

### Python

**Debian / Ubuntu / Mac**
```
curl -O https://www.python.org/ftp/python/3.10.6/Python-3.10.6.tar.xz
tar -xf Python-3.*
cd Python-3.*
./configure --enable-optimizations
make -j 4
sudo make altinstall
```

**Windows**
Download and install [Python](https://www.python.org/downloads/).

### Node

**Debian / Ubuntu / Mac**
```
curl -sL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt-get install nodejs
```

**Windows**
Download and install [Node](https://nodejs.org/en/download/).

### Poetry
This project uses [Poetry](https://python-poetry.org/docs/) for dependency management and packaging.

Install Poetry and add Poetry to [Path](https://python-poetry.org/docs/#installation).

**Debian / Ubuntu / Mac**

`curl -sSL https://install.python-poetry.org | python3 -`

**Windows**

open powershell and run: `(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -`

## Development

### Dev Setup
Install dependencies: `poetry install`

Install the defined pre-commit hooks: `poetry run pre-commit install`

Activate the virtualenv: `poetry shell`

Run the Django dev server: `./manage.py runserver` or `python manage.py runserver`

