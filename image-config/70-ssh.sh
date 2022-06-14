#!/bin/bash -x
set -eo pipefail

pushd /etc/ssh
ssh-keygen -A
popd
