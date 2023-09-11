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

import structlog
from orchestrator.domain import SubscriptionModel

from products.product_blocks.node import NodeBlockProvisioning

from services.netbox import NetboxNodePayload, netbox_get_ip

logger = structlog.get_logger(__name__)


def build_node_payload(model: NodeBlockProvisioning, subscription: SubscriptionModel) -> NetboxNodePayload:
    """Create and return an Netbox payload object for a :class:`~products.product_blocks.node.NodeBlockProvisioning`.

    It makes calls to CRM and IMS to construct the object correctly.

    Example payload::

        {
           "id": 11,
           "name": "loc5-core",
           "status": "active",
           "primary_ip4": 8,
           "primary_ip6": 11
        }

    Args:
        model: NodeBlockProvisioning
        subscription: The Subscription that will be changed

    Returns: :class:`Record`

    """
    if not model.node_id:
        raise ValueError("Build node payload not implemented for new nodes")

    logger.info("in build_node_payload()")

    return NetboxNodePayload(
        id=model.node_id,
        name=model.node_name,
        status=model.node_status,
        primary_ip4=netbox_get_ip(str(model.ipv4_loopback)).id,
        primary_ip6=netbox_get_ip(str(model.ipv6_loopback)).id,
    )
