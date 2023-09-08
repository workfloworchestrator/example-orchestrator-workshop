# Copyright 2019-2023 SURF.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from typing import List

import pynetbox  # type: ignore
import structlog
from pynetbox.models.dcim import Devices
from pynetbox.models.ipam import IpAddresses

from products.services.netbox.payload.netbox_payload import NetboxPayload

logger = structlog.get_logger(__name__)

netbox = pynetbox.api(
    "http://netbox:8080",
    token="e744057d755255a31818bf74df2350c26eeabe54",
)  # fmt: skip


def netbox_get_node(name: str) -> Devices:
    """
    Get device from Netbox identified by id.
    """
    return netbox.dcim.devices.get(name=name)


def netbox_get_planned_nodes_list() -> List[Devices]:
    """
    Get list of devices from netbox that are in planned state.
    """
    logger.debug("Connecting to Netbox to get list of available nodes")
    node_list = list(netbox.dcim.devices.filter(status="planned"))
    logger.debug("Found nodes in Netbox", amount=len(node_list))
    return node_list


def netbox_get_ip(address: str) -> IpAddresses:
    """
    Get IP address from Netbox identified by address.
    """
    return netbox.ipam.ip_addresses.get(address=address)


def netbox_create_or_update(payload: NetboxPayload) -> bool:
    """
    Create or update object on payload.endpoint in Netbox.

    Args:
        payload: values to update object with on payload.endpoint

    Returns:
         True if the object was updated, False otherwise
    """
    if not payload.id:
        raise ValueError("Create devices object in Netbox not implemented")

    if payload.endpoint == 'devices':
        endpoint = netbox.dcim.devices
    else:
        raise ValueError(f"Netbox endpoint {payload.endpoint} not implemented")

    if not (netbox_object := endpoint.get(payload.id)):
        raise ValueError(f"Netbox object with id {payload.id} on endpoint {payload.endpoint} not found")

    update_dict = payload.dict()
    update_dict.pop("endpoint")  # remove because it is not a genuine Netbox Endpoint object
    netbox_object.update(update_dict)
    return netbox_object.save()
