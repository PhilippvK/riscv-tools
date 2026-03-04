#!/bin/bash

set -e

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]:-${(%):-%N}}" )" &> /dev/null && pwd )
TOP_DIR=$(dirname $SCRIPT_DIR)
IMAGE=philippvk/riscv-tools
VERSION=${1:-"20.04"}
BASE_IMAGE=ubuntu:$VERSION
TAG=ubuntu-${VERSION}

echo $DOCKER_PREFIX docker build -t $IMAGE:$TAG -f $TOP_DIR/docker/Dockerfile_ubuntu $TOP_DIR --build-arg BASE_IMAGE=$BASE_IMAGE
$DOCKER_PREFIX docker build -t $IMAGE:$TAG -f $TOP_DIR/docker/Dockerfile_ubuntu $TOP_DIR --build-arg BASE_IMAGE=$BASE_IMAGE
