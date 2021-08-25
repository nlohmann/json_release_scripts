#!/usr/bin/env bash
set -euxo pipefail

test -d workdir/json || scripts/clone/git-flow-clone https://github.com/nlohmann/json.git workdir/json

cd workdir/json ; git config gitflow.prefix.versiontag v
