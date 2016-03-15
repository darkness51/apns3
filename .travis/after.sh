#!/bin/bash

PYENV_ROOT="$HOME/.pyenv"
PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
pyenv local $PYTHON_VERSION
pyenv global $PYTHON_VERSION

ENV=$HOME/env
source $ENV/bin/activate

coveralls
