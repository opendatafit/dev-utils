#!/usr/bin/env python

# Create a user

import os
import sys

import pymongo

from pathlib import Path

# Import create_or_return_user test helper from users repo
sys.path.append(os.environ.get("ODF_USERS_SRC") + "/tests")
from helpers import create_or_return_user  # noqa: E402


_, EMAIL, PASSWORD, FIRST_NAME, LAST_NAME, MUGSHOT = sys.argv


# These environment variables are set from dev-utils run scripts currently
# This is a temp hack, will be set by direnv in future
# Currently in production (maintenance box) we will have to set them manually
MONGO_URI = os.environ.get("MONGO_URI") # Externally accessible Mongo DB URI
USERS_DBNAME = os.environ.get("USERS_DBNAME")
USERS_COLNAME = os.environ.get("USERS_COLNAME")

# Connect to DB
client = pymongo.MongoClient(MONGO_URI)

if MUGSHOT:
    mugshot = Path(MUGSHOT).read_text()

# Create user
create_or_return_user(
    collection=client[USERS_DBNAME][USERS_COLNAME],
    email=EMAIL,
    password=PASSWORD,
    first_name=FIRST_NAME,
    last_name=LAST_NAME,
    mugshot=mugshot,
)
