#!/usr/bin/env bash

# Requires opendatafit/store to be running and accessible on network

# To invoke function:
# curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{"workspace":"[workspace ID]","algorithm":null}'

docker run -p 9000:8080 --network=store-network --env LOCAL_LAMBDA=1 opendatafit/execution-base
