#!/usr/bin/env bash

docker run --env LOCAL_EXEC=1 --env "LOCAL_ARGS=$(cat ./input.json)" opendatafit/execution-base
