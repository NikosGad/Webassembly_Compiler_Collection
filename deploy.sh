#!/usr/bin/env bash

if [[ -d /results ]]
then
    echo "/results exists on your filesystem."
    echo "Please move its contents to another directory and remove the directory, so that the deployment can continue."
    echo "Exiting..."
    exit 1
fi

docker-compose up

exit 0
