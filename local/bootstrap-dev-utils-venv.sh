#!/usr/bin/env bash
  
cd "$ODF_SERVICES_ROOT/dev-utils"

direnv allow .
 
pip install -r "${ODF_STORE_SRC}/requirements.txt" # App requirements (from lockfile)
