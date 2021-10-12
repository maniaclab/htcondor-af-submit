#!/bin/bash -x
set -eo pipefail
# This script does not do significant (any) error checking.

###############################################################################
# Grab the connect provisioner 
CONNECT_DIR='/usr/local/ciconnect'
mkdir -p $CONNECT_DIR
curl -L https://raw.githubusercontent.com/maniaclab/ci-connect-api/master/resources/provisioner/sync_users.sh > $CONNECT_DIR/sync_users.sh
chmod +x $CONNECT_DIR/sync_users.sh

# do a one-time run at startup
pushd $CONNECT_DIR
$CONNECT_DIR/sync_users.sh -u root.atlas-af -g root.atlas-af -e https://api.ci-connect.net:18080 >> /var/log/provisioner.log 2>&1
popd

echo "export API_TOKEN=$API_TOKEN" >> $CONNECT_DIR/config
