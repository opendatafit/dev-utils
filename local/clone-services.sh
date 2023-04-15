#!/usr/bin/env bash

cd "$ODF_SERVICES_ROOT"

git clone git@github.com:opendatafit/users.git && \
git clone git@github.com:opendatafit/execution-base.git && \
git clone git@github.com:opendatafit/scheduler.git && \
git clone git@github.com:opendatafit/jobjockey.git && \
git clone git@github.com:opendatafit/store.git
