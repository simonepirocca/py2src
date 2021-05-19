#!/bin/bash
CLONE_URL=$1
CLONE_DIR=$2
if [[ ! -z "$CLONE_URL" ]] && [[ ! -z "$CLONE_DIR" ]]
then
    cd ../cloned_repos 
    if [ -f "./$CLONE_DIR" ]; then rm ../$CLONE_DIR; fi
    git clone -n $CLONE_URL 
    echo "CLONED" 
fi
