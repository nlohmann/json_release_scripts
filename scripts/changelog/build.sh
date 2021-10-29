#!/usr/bin/env bash
set -euxo pipefail

# find GNU sed to use "-i" parameter
SED=$(command -v gsed || which sed)

# read config
VERSION_MAJOR=$(jq --raw-output ".VERSION_MAJOR" < ../../config.json)
VERSION_MINOR=$(jq --raw-output ".VERSION_MINOR" < ../../config.json)
VERSION_PATCH=$(jq --raw-output ".VERSION_PATCH" < ../../config.json)
NEXT_VERSION="$VERSION_MAJOR.$VERSION_MINOR.$VERSION_PATCH"

# create raw ChangeLog.md
CHANGELOG_GITHUB_TOKEN=$(jq --raw-output ".GITHUB_TOKEN" < ../../config.json) /Users/niels/.gem/ruby/2.6.0/bin/github_changelog_generator -o ChangeLog.md --user nlohmann --project json --simple-list --release-url https://github.com/nlohmann/json/releases/tag/%s --future-release $NEXT_VERSION

# fix links
$SED -i 's|https://github.com/nlohmann/json/releases/tag/HEAD|https://github.com/nlohmann/json/tree/HEAD|' ChangeLog.md

# add header
$SED -i '2i All notable changes to this project will be documented in this file. This project adheres to [Semantic Versioning](http://semver.org/).' ChangeLog.md
