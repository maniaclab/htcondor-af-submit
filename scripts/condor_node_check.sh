#!/bin/bash
### GET THE NODE NAME FIRST
full_node=$(hostname)
IFS='.' read -r nodename af uchi edu <<< "${full_node}"

/bin/sysclient online "${nodename}"
/bin/condor_node_check --config-file /etc/sysview/sysview.ini
