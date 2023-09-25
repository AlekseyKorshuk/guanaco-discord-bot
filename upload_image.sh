#!/bin/bash

set -e

# Check for sufficient number of arguments
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <GIT_USERNAME> <GIT_TOKEN>"
    exit 1
fi

GIT_USERNAME="$1"
GIT_TOKEN="$2"

IMAGE="gcr.io/chai-959f8/guanaco-discord-bot:latest"
echo "Building image '$IMAGE'"

docker build --build-arg GIT_USERNAME="$GIT_USERNAME" --build-arg GIT_TOKEN="$GIT_TOKEN" -t "$IMAGE" --platform linux/amd64 .
docker push "$IMAGE"
