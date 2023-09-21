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

from functools import singledispatch
from typing import Union

from orchestrator.domain.base import ProductBlockModel, ProductModel, SubscriptionModel

from products.product_blocks.circuit import CircuitBlockInactive, Layer3InterfaceInactive
from products.product_types.circuit import CircuitProvisioning
from products.product_types.node import NodeInactive
from utils.singledispatch import single_dispatch_base


@singledispatch
def description(model: Union[ProductModel, ProductBlockModel, SubscriptionModel]) -> str:
    """Build subscription description (generic function).

    Specific implementations of this generic function will specify the model types they work on.

    Args:
        model: Domain model for which to construct a description.

    Returns:
    ---
        The constructed description.

    Raises:
    --
        TypeError: in case a specific implementation could not be found. The domain model it was called for will be
            part of the error message.

    """
    return single_dispatch_base(description, model)


@description.register
def node_product_description(node: NodeInactive) -> str:
    return f"Node {node.node.node_name}"


@description.register
def layer3interface_product_block_description(layer3interface: Layer3InterfaceInactive) -> str:
    """
    layer3interface_product_block_description creates an interface description that is used by The Orchestrator
    and any system that needs to generate an interface description. This function holds the
    business logic for doing so.

        layer3interface.port.node.node_name (str): This is the name of the device on the far
            side of the circuit from this interface's perspective. (i.e. loc2-core)
        layer3interface.port.port_name (str): This is the name of the port on the far side of
            the circuit from this interface's perspective. (i.e. 1/1/c1/1)

    Returns:
        str: The assembled interface description. Given the examples above this function would return:
        "Circuit Connection to loc2-core port 1/1/c1/1"
    """
    return f"Circuit Connection to {layer3interface.port.node.node_name} port {layer3interface.port.port_name}"


@description.register
def circuit_product_block_description(circuit: CircuitBlockInactive) -> str:
    """
    circuit_product_block_description creates a circuit block description that is used by The Orchestrator
    and any system that needs to generate a circuit description. This function holds the
    business logic for doing so.

         circuit.members[0].port.node.node_name (str): This is the name of the device on the "A" side of the
         circuit. For netbox's API, this is the first item in the list of circuit endpoints. (i.e. loc1-core)

         circuit.members[0].port.port_name (str): This is the name of the port on the "A" side of the circuit.
         For netbox's API, this is the first item in the list of circuit endpoints. (i.e. 1/1/c2/1)

         circuit.members[1].port.node.node_name (str): This is the name of the device on the "B" side of the circuit.
         For netbox's API, this is the second item in the list of circuit endpoints. (i.e. loc2-core)

        circuit.members[1].port.port_name (str): This is the name of the port on the "B" side of the circuit. For
        netbox's API, this is the first item in the list of circuit endpoints. (i.e. 1/1/c1/1)

    Returns:
        str: The assembled circuit block description. Given the examples above this function would return:
        loc1-core:1/1/c2/1 <--> loc2-core:1/1/c1/1"
    """
    a_side = f"{circuit.members[0].port.node.node_name}:{circuit.members[0].port.port_name}"
    b_side = f"{circuit.members[1].port.node.node_name}:{circuit.members[1].port.port_name}"
    return f"{a_side} <--> {b_side}"


@description.register
def circuit_product_description(circuit: CircuitProvisioning) -> str:
    """
    circuit_product_description creates a circuit subscription description. This function holds the
    business logic for doing so.

        circuit.circuit.circuit_id (int): This is the circuit ID that is in netbox. This is a unique
            integer to this circuit. (i.e. 7)

        circuit.circuit.circuit_description (str): The circuit block description
    Returns:
        str: The assembled circuit subscription description. Given the examples above this function would return:
        "Circuit ID 7: loc1-core:1/1/c2/1 <--> loc2-core:1/1/c1/1"
    """
    return f"Circuit ID {circuit.circuit.circuit_id}: {circuit.circuit.circuit_description}"
