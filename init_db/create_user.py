#!/usr/bin/env python

# Create a user

import os
import sys

import pymongo

from pathlib import Path

# Import create_user test helper from users repo
sys.path.append(os.environ.get("ODF_USERS_SRC") + "/tests")
from helpers import create_user  # noqa: E402

# Import app configs from store repo
sys.path.append(os.environ.get("ODF_STORE_SRC"))
from app.config import DevelopmentConfig, TestingConfig, ProductionConfig


_, EMAIL, PASSWORD, FIRST_NAME, LAST_NAME, MUGSHOT = sys.argv


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

if MUGSHOT:
    mugshot = Path(MUGSHOT).read_text()

# Create user
create_user(
    collection=client[USERS_DBNAME][USERS_COLNAME],
    email=EMAIL,
    password=PASSWORD,
    first_name=FIRST_NAME,
    last_name=LAST_NAME,
    mugshot=mugshot,
)
