#!/bin/sh
# NOTE: Can't currently use --ssh option with docker-compose
# Need to build store & users containers separately before executing
# (they pull in private git repo via ssh in pip requirements)
# See issue: https://github.com/docker/compose/issues/7184

(cd $ODF_STORE_SRC && ./build_dockerfile.sh)
(cd $ODF_USERS_SRC && ./build_dockerfile.sh)
COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker compose build $@
