#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

cp -v "$SCRIPT_DIR/icons/$1" "$SCRIPT_DIR/icons/$2"
cp -v "$SCRIPT_DIR/banners/$1" "$SCRIPT_DIR/banners/$2"
cp -v "$SCRIPT_DIR/tenaldo_square/$1" "$SCRIPT_DIR/tenaldo_square/$2"
