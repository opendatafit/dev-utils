#!/usr/bin/env bash

docker run \
  --env LOCAL_EXEC=1 \
  -v "$(pwd)"/input-data:/input-data \
  opendatafit/execution-base
