#!/usr/bin/env bash

SERVICES=("execution-base" "jobjockey" "scheduler" "store" "users")

printf "$ODF_SERVICES_ROOT\n"

for name in ${SERVICES[@]}; do
  SERVICE_PATH="$ODF_SERVICES_ROOT/$name"
  cd $SERVICE_PATH
  
  printf "$(pwd)\n"
  direnv allow .

  # Install requirements
  pip install -r requirements.txt # App requirements (from lockfile)
  pip install ".[development]" # Development requirements
  
  # Set up pre-commit pipeline
  pre-commit install
  pre-commit run

  # drop back to odf services
  cd $ODF_SERVICES_ROOT
done
