#!/bin/bash
set -eo pipefail

echo "# This file was created by $prog" > /etc/condor/config.d/01-env.conf
add_values_to 01-env.conf \
    CONDOR_HOST "${CONDOR_SERVICE_HOST:-${CONDOR_HOST:-\$(FULL_HOSTNAME)}}" \
    NUM_CPUS "${NUM_CPUS:-1}" \
    MEMORY "${MEMORY:-1024}" \
    RESERVED_DISK "${RESERVED_DISK:-1024}" \
    USE_POOL_PASSWORD "${USE_POOL_PASSWORD:-no}"
