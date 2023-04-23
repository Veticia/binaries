#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# append .png to a filename if it's not present
function add_png {
    filename=$1
    if [[ ! "$filename" =~ \.png$ ]]; then
        filename="${filename}.png"
    fi
    echo "$filename"
}

old=$(add_png "$1")
new=$(add_png "$2")

cp -v "$SCRIPT_DIR/icons/$old" "$SCRIPT_DIR/icons/$new"
cp -v "$SCRIPT_DIR/banners/$old" "$SCRIPT_DIR/banners/$new"
cp -v "$SCRIPT_DIR/tenaldo_square/$old" "$SCRIPT_DIR/tenaldo_square/$new"
