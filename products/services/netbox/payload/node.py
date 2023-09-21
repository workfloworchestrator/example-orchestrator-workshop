# Copyright 2019 - 2023 SURF.
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
# from dataclasses import dataclass

from orchestrator.domain import SubscriptionModel

from products.product_blocks.node import NodeBlockProvisioning
from services import netbox


def build_node_payload(model: NodeBlockProvisioning, subscription: SubscriptionModel) -> netbox.DevicePayload:
    """Create and return a Netbox payload object for a :class:`~products.product_blocks.node.NodeBlockProvisioning`.

    Example payload::

        {
           "id": 7,
           "name": "loc1-core",
           "site": 1,
           "status": "active",
           "device_role": 1,
           "device_type": 1,
           "primary_ip4": 2,
           "primary_ip6": 3
        }

    Args:
        model: NodeBlockProvisioning
        subscription: The Subscription that will be changed

    Returns: :class:`netbox.DevicePayload`

    """
    if not model.node_id:
        raise ValueError("Build node payload not implemented for new nodes")

    # device is not created by the orchestrator, fetch needed fields from Netbox
    device = netbox.get_device(model.node_name)

    return netbox.DevicePayload(
        site=device.site.id,  # not yet administrated in orchestrator
        device_type=device.device_type.id,  # not yet administrated in orchestrator
        device_role=device.device_type.id,  # not yet administrated in orchestrator
        id=model.node_id if model.node_id else -1,
        name=model.node_name,
        status=model.node_status,
        primary_ip4=netbox.get_ip_address(str(model.ipv4_loopback)).id,
        primary_ip6=netbox.get_ip_address(str(model.ipv6_loopback)).id,
    )
