# Usage: source load_env.sh store.test.env
export $(cat $ODF_DEV_UTILS_SRC/$@ | xargs)
