#!/usr/bin/env bash
set -euxo pipefail

# read config
VERSION_MAJOR=$(jq --raw-output ".VERSION_MAJOR" < ../../config.json)
VERSION_MINOR=$(jq --raw-output ".VERSION_MINOR" < ../../config.json)
VERSION_PATCH=$(jq --raw-output ".VERSION_PATCH" < ../../config.json)
NEXT_VERSION="$VERSION_MAJOR.$VERSION_MINOR.$VERSION_PATCH"

cd ../../workdir/json

git flow release finish $NEXT_VERSION

git checkout master
git pull
git push

git checkout develop
git pull
git push
