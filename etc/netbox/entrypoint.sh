#!/bin/bash

if [ -f "/etc/netbox/data.json" ]; then
    echo "Loading data from  /etc/netbox/data.json"
    /opt/netbox/netbox/manage.py loaddata -v 3 /etc/netbox/data.json
else
    echo "no data to load"
fi

/opt/netbox/launch-netbox.sh