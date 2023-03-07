#!/bin/sh

if ps -p $SSH_AGENT_PID > /dev/null
then
    echo "ssh-agent running."
else
    echo "ssh-agent not running. Starting ssh-agent."
    eval $(ssh-agent)
fi

echo "Ensure you add your key with ssh-add ~/.ssh/[your key] or you will get ssh errors during build."

COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker compose build --ssh default=$SSH_AUTH_SOCK $@
