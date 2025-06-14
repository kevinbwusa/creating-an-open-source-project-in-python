#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )" # See https://stackoverflow.com/a/246128/1394393
SRC_DIR=${DIR%%/}/src

if [ ! -v PYTHONPATH ]; then
    export PYTHONPATH=$SRC_DIR
    echo "Created PYTHONPATH as $SRC_DIR"
elif [[ "$PYTHONPATH" == *"$SRC_DIR"* ]]; then
    echo "$SRC_DIR already PYTHONPATH"
else 
    export PYTHONPATH="$PYTHONPATH:$SRC_DIR"
    echo "Added $SRC_DIR to PYTHONPATH"
fi
