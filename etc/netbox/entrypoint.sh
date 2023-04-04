#!/bin/bash

if [ -f "/etc/netbox/data.json" ]; then
    echo "Loading data from  /etc/netbox/data.json"
    /opt/netbox/netbox/manage.py loaddata -v 3 /etc/netbox/data.json
fi

/opt/netbox/docker-entrypoint.sh /opt/netbox/launch-netbox.sh