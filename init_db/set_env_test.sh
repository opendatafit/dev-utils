# Usage: source set_env_test.sh
# Temporarily set development env vars
# Will be set by direnv in future
# Ideally we want these in a central location, not repeated inside compose.yml
export MONGO_URI="mongodb://opendatafit:password@localhost:27017/"
export MONGO_DBNAME="opendatafit-store-test"
export USERS_DBNAME="opendatafit-users-test"
export USERS_COLNAME="users"
