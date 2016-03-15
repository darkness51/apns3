#!/bin/bash

PYENV_ROOT="$HOME/.pyenv"
PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"

ENV=$HOME/env
source $ENV/bin/activate

make test
make flake8
