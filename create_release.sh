#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Illegal number of parameters"
    exit 1
fi


DIR=$1
echo "DIR=$DIR"

NAME=$(basename $DIR)
echo "NAME=$NAME"

TAG=${NAME//gcc/gnu}
echo "TAG=$TAG"

gh release create $TAG --title "$(cat $DIR/label.txt)" $DIR/*.tar.xz --notes ""
