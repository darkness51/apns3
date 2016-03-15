#!/bin/bash

set -ex

PYENV_ROOT="$HOME/.pyenv"
git clone https://github.com/yyuu/pyenv.git $PYENV_ROOT
PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
pyenv install $PYTHON_VERSION -s
pyenv local $PYTHON_VERSION
pyenv global $PYTHON_VERSION
pyenv rehash
which python
python --version
pip install --upgrade pip virtualenv

ENV=$HOME/env
virtualenv $ENV
source $ENV/bin/activate
echo $VIRTUAL_ENV
python --version

pip install coveralls

openssl version -a
python -c 'import ssl; print(ssl.OPENSSL_VERSION)'
python -c 'import ssl; print(ssl.HAS_NPN)'
python -c 'import ssl; print(ssl.HAS_ALPN)'
make depends
python -c 'from OpenSSL import SSL; print(SSL.SSLeay_version(SSL.SSLEAY_VERSION))'
