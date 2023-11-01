#!/bin/bash
set -e

CWD=$(cd $(dirname $0); pwd)

REGISTRY=${REGISTRY:-index.docker.io}
IMAGE=${REGISTRY}/gistapi:${RELEASE:-latest}

echo Building $IMAGE
docker build \
    --force-rm \
    --rm=true \
    -f "$CWD/Dockerfile" \
    --build-arg REGISTRY=$REGISTRY \
    -t $IMAGE \
    "$CWD/.."
