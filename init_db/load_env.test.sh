# Usage: source load_env.test.sh

source $ODF_DEV_UTILS_SRC/load_env.sh store.test.env

# Override MONGO_URI for external access
export MONGO_URI="mongodb://opendatafit:password@localhost:27017/"
