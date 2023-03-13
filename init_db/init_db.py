#!/usr/bin/env python

# Initialise DB with default opendatafit user and datapackages

import os
import sys
import pymongo
import json
from pathlib import Path

# Import helpers and configs from store repo
sys.path.append(os.environ.get("ODF_STORE_SRC"))
from app.helpers import create_datapackage
from app.config import DevelopmentConfig, TestingConfig, ProductionConfig

sys.path.append(os.environ.get("ODF_USERS_SRC") + "/tests")
from helpers import create_user  # noqa: E402


if os.environ.get("APP_ENV") == "production":
    MONGO_URI = os.environ.get("MONGO_URI")
    MONGO_DBNAME = ProductionConfig.MONGO_DBNAME
    USERS_DBNAME = ProductionConfig.USERS_DBNAME
    USERS_COLNAME = ProductionConfig.USERS_COLNAME
else:
    MONGO_URI = TestingConfig.MONGO_URI
    MONGO_DBNAME = DevelopmentConfig.MONGO_DBNAME
    USERS_DBNAME = TestingConfig.USERS_DBNAME
    USERS_COLNAME = TestingConfig.USERS_COLNAME


# Connect to DB
client = pymongo.MongoClient(MONGO_URI)
db = client[MONGO_DBNAME]

mugshot = Path("./mugshots/opendatafit.base64").read_text()

# Create opendata.fit user
opendatafit = create_user(
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
