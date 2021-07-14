#!/bin/bash
set -eo pipefail

echo "# This file was created by $prog" > /etc/condor/config.d/01-env.conf
echo "${CONDOR_SERVICE_HOST:-${CONDOR_HOST:-\$(FULL_HOSTNAME)}}" >> /etc/condor/config.d/01-env.conf
