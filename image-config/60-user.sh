#!/bin/bash
set -eo pipefail
# This script does not do significant (any) error checking.

###############################################################################
# Grab the connect provisioner 
CONNECT_DIR='/usr/local/etc/ciconnect'
mkdir -p $CONNECT_DIR
curl -L https://raw.githubusercontent.com/maniaclab/ci-connect-api/master/resources/provisioner/sync_users.sh > $CONNECT_DIR/sync_users.sh
chmod +x $CONNECT_DIR/sync_users.sh
