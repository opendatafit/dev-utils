#!/usr/bin/env python

# Initialise DB with default opendatafit user and datapackages

import os
import sys
import pymongo
import json
from pathlib import Path

sys.path.append(os.environ.get("ODF_STORE_SRC"))
from app.helpers import create_datapackage

sys.path.append(os.environ.get("ODF_USERS_SRC") + "/tests")
from helpers import create_or_return_user  # noqa: E402


# These environment variables are set from dev-utils run scripts currently
# This is a temp hack, will be set by direnv in future
# Currently in production (maintenance box) we will have to set them manually
MONGO_URI = os.environ.get("MONGO_URI") # Externally accessible Mongo DB URI
MONGO_DBNAME = os.environ.get("MONGO_DBNAME")
USERS_DBNAME = os.environ.get("USERS_DBNAME")
USERS_COLNAME = os.environ.get("USERS_COLNAME")

# Connect to DB
client = pymongo.MongoClient(MONGO_URI)
db = client[MONGO_DBNAME]

mugshot = Path("./mugshots/opendatafit.base64").read_text()

# Create master opendata.fit user
opendatafit = create_or_return_user(
    collection=client[USERS_DBNAME][USERS_COLNAME],
    email="opendatafit@proton.me",
    password="password",
    first_name="opendata.fit",
    last_name="",
    mugshot=mugshot,
)

# Create SAS datapackage
with open("./datapackage_sas.json") as f:
    datapackage = json.load(f)

datapackage_id = create_datapackage(
    db=db,
    datapackage=datapackage,
    user_id=opendatafit["id"],
    view_permission="public",
)

print("Created datapackage:", datapackage_id)
