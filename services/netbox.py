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
from dataclasses import asdict, dataclass
from functools import singledispatch
from typing import Any, List

import pynetbox  # type: ignore
import structlog
from pynetbox.models.dcim import Devices
from pynetbox.models.ipam import IpAddresses

from utils.singledispatch import single_dispatch_base

logger = structlog.get_logger(__name__)

netbox = pynetbox.api(
    "http://netbox:8080",
    token="e744057d755255a31818bf74df2350c26eeabe54",
)  # fmt: skip


@dataclass
class NetboxPayload:
    id: int  # all objects on any endpoint have a unique id

    def dict(self):
        return asdict(self)


@dataclass
class NetboxNodePayload(NetboxPayload):
    name: str
    status: str
    primary_ip4: int
    primary_ip6: int


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


@singledispatch
def netbox_create_or_update(payload: NetboxPayload, **kwargs: Any) -> bool:
    """Create or update object described by payload in Netbox (generic function).

    Specific implementations of this generic function will specify the payload types they work on.

    Args:
        payload: Netbox object specific payload.

    Returns:
        True if the object was created or updated successfully in Netbox, False otherwise.

    Raises:
        TypeError: in case a specific implementation could not be found. The payload it was called for will be
            part of the error message.

    """
    return single_dispatch_base(netbox_create_or_update, payload)


@netbox_create_or_update.register
def _(payload: NetboxNodePayload, **kwargs: Any) -> bool:
    return netbox_create_or_update_node(payload)


def netbox_create_or_update_node(payload: NetboxNodePayload) -> bool:
    """
    Create or update a node in Netbox.

    Args:
        payload: values to create or update node with

    Returns:
         True if the node was created or updated, False otherwise
    """
    if not payload.id:  # create object in Netbox
        raise ValueError("Create node object in Netbox not implemented")
    else:  # update object in Netbox
        if not (device := netbox.dcim.devices.get(payload.id)):
            raise ValueError(f"Netbox object with id {payload.id} on netbox devices endpoint not found")
        device.update(payload.dict())
        return device.save()
