#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
. $DIR/../venv/bin/activate
python $DIR/abe.py ${@:1}
