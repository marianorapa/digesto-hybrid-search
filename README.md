# Ubuntu Setup (Run)

## Install Docker

https://docs.docker.com/engine/install/ubuntu/

## Run Container

docker run agustinnormand/digesto-hybrid-search:0.0.3

# Ubuntu Setup (Build)

## Install PyEnv
Source: https://medium.com/@aashari/easy-to-follow-guide-of-how-to-install-pyenv-on-ubuntu-a3730af8d7f0

sudo apt update
sudo apt install -y make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
curl https://pyenv.run | bash

### Add pyenv to path

### Confirm Instalation:

pyenv --version

## Install Poetry
Source: https://python-poetry.org/docs/#installing-with-the-official-installer

curl -sSL https://install.python-poetry.org | python3 -

### Add poetry to path

### Confirm Installation

poetry --version

### Activate Virtual Envs with poetry
Source: https://python-poetry.org/docs/managing-environments/

poetry config virtualenvs.prefer-active-python true

## Install Java

sudo apt update -y && sudo apt upgrade -y

sudo apt install openjdk-21-jdk -y

Set JAVA_HOME environment variable

## Clone repository

git clone https://github.com/marianorapa/digesto-hybrid-search.git

## Setup environment

Start shell:
poetry shell

Install lock dependencies:
poetry install

python3 main.py

## Build Container

### Clear environment with main.py menu option

### Clear python Cache Files

find . | grep -E "(/__pycache__$|\.pyc$|\.pyo$)" | xargs rm -rf

docker build -t agustinnormand/digesto-hybrid-search:0.0.3 .
