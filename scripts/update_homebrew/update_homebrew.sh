#!/usr/bin/env bash
set -euxo pipefail

# read config
VERSION_MAJOR=$(jq --raw-output ".VERSION_MAJOR" < ../../config.json)
VERSION_MINOR=$(jq --raw-output ".VERSION_MINOR" < ../../config.json)
VERSION_PATCH=$(jq --raw-output ".VERSION_PATCH" < ../../config.json)
NEXT_VERSION="$VERSION_MAJOR.$VERSION_MINOR.$VERSION_PATCH"

rm -fr v$NEXT_VERSION.tar.gz

wget https://github.com/nlohmann/json/archive/v$NEXT_VERSION.tar.gz
SHA256=$(sha256sum v3.10.2.tar.gz | awk '{print $1}')

brew bump-formula-pr --strict nlohmann-json --url=https://github.com/nlohmann/json/archive/v$NEXT_VERSION.tar.gz --sha256=$SHA256

rm -fr v$NEXT_VERSION.tar.gz
