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
from typing import Any, List, Optional

import structlog
from pynetbox import api
from pynetbox.core.endpoint import Endpoint
from pynetbox.core.query import RequestError
from pynetbox.models.dcim import Devices
from pynetbox.models.ipam import IpAddresses

from utils.singledispatch import single_dispatch_base

logger = structlog.get_logger(__name__)

netbox = api(
    "http://netbox:8080",
    token="e744057d755255a31818bf74df2350c26eeabe54",
)  # fmt: skip


@dataclass
class NetboxPayload:
    id: int  # all objects on any endpoint have a unique id

    # return payload as a dict that is suitable to be used on pynetbox .create() or .updates().
    def dict(self):
        return asdict(self)


@dataclass
class NetboxDevicePayload(NetboxPayload):
    # mandatory fields to create Devices object in Netbox:
    site: int
    device_type: int
    device_role: int
    # optional fields:
    name: Optional[str]
    status: Optional[str]
    primary_ip4: Optional[int]
    primary_ip6: Optional[int]


def netbox_get_device(name: str) -> Devices:
    """
    Get device from Netbox identified by name.
    """
    return netbox.dcim.devices.get(name=name)


def netbox_get_devices(status: Optional[str] = None) -> List[Devices]:
    """
    Get list of Devices objects from netbox, optionally filtered by status.
    """
    logger.debug("Connecting to Netbox to get list of devices")
    if status:
        node_list = list(netbox.dcim.devices.filter(status=status))
    else:
        node_list = list(netbox.dcim.devices.all())
    logger.debug("Found nodes in Netbox", amount=len(node_list))
    return node_list


def netbox_get_ip_address(address: str) -> IpAddresses:
    """
    Get IP IpAddress object from Netbox identified by address.
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
def _(payload: NetboxDevicePayload, **kwargs: Any) -> bool:
    return _netbox_create_or_update_object(payload, endpoint=netbox.dcim.devices)


def _netbox_create_or_update_object(payload: NetboxDevicePayload, endpoint: Endpoint) -> bool:
    """
    Create or update an object in Netbox.

    Args:
        payload: values to create or update object
        endpoint: a Netbox Endpoint

    Returns:
         True if the node was created or updated, False otherwise
    """
    if not payload.id:
        try:
            endpoint.create(payload.dict())
        except RequestError as exc:
            logger.warning("Netbox create failed", payload=payload, exc=str(exc))
            return False
        else:
            return True
    else:
        if not (object := endpoint.get(payload.id)):
            raise ValueError(f"Netbox object with id {payload.id} on netbox {endpoint.name} endpoint not found")
        object.update(payload.dict())
        return object.save()
