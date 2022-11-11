#!/bin/bash
# NOTE: Can't currently use --ssh option with docker-compose
# Need to build opendatafit-store container separately before executing
# See issue: https://github.com/docker/compose/issues/7184

(cd $OPENDATAFIT_STORE_SRC && ./build_dockerfile.sh)
COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker-compose build $@
