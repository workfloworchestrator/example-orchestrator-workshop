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

from products.product_blocks.circuit import CircuitBlockProvisioning
from services.netbox import NetboxCablePayload, NetboxCableTerminationPayload


def build_circuit_payload(model: CircuitBlockProvisioning, subscription: SubscriptionModel) -> NetboxCablePayload:
    """Create and return a Netbox payload object for a :class:`~products.product_types.circuit.CircuitInactive`.

    Example payload::

        {
           "id": 3,
           "status": "planned",
           "description": "Circuit ID 3: loc1-core:1/1/c7/1 <--> loc2-core:1/1/c7/1",
           "a_terminations": [
              {
                 "object_id": 43,
                 "object_type": "dcim.interface"
              }
           ],
           "b_terminations": [
              {
                 "object_id": 115,
                 "object_type": "dcim.interface"
              }
           ]
        }

    Args:
        model: CircuitInactive
        subscription: The Subscription that will be changed

    Returns: :class:`NetboxCablePayload`
    """
    return NetboxCablePayload(
        id=model.circuit_id if model.circuit_id else -1,
        status=model.circuit_status,
        description=model.circuit_description,
        a_terminations=[NetboxCableTerminationPayload(object_id=model.members[0].port.port_id)],
        b_terminations=[NetboxCableTerminationPayload(object_id=model.members[1].port.port_id)],
    )
