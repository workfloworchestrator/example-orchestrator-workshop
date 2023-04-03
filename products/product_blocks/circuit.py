from typing import TypeVar
from uuid import UUID

from orchestrator.domain.base import ProductBlockModel, SubscriptionInstanceList
from orchestrator.types import SubscriptionLifecycle
from node import Node
# Product Block definitions for Backbone Link Service

# Constrained lists for models

T = TypeVar("T", covariant=True)


class ListOfMembers(SubscriptionInstanceList[T]):
    min_items = 1
    max_items = 16


class PortPair(SubscriptionInstanceList[T]):
    min_items = 2
    max_items = 2

class CircuitState(Choice):
    UP = "up"
    DOWN = "down"

# Port


class PortInactive(ProductBlockModel, product_block_name="Port"):
    """Object model for a Port as used by
    Backbone Link Service"""

    port_id: int
    port_description: str
    node: Node


class PortProvisioning(
    PortInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """Port with fields for use in the provisioning lifecycle"""

    port_id: int
    port_description: str
    node: Node


class Port(PortProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """Port with fields for use in the provisioning lifecycle"""

    port_id: int
    port_description: str
    node: Node


# Layer 3 Interface


class Layer3InterfaceInactive(ProductBlockModel, product_block_name="Layer 3 Interface"):
    """Object model for a Layer 3 Interface as used by Circuit"""

    v6_ip_address: str


class Layer3InterfaceProvisioning(
    Layer3InterfaceInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """Layer 3 Interface with fields for use in the provisioning lifecycle"""

    v6_ip_address: str


class Layer3Interface(Layer3InterfaceProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """Layer 3 Interface with fields for use in the active lifecycle"""

    v6_ip_address: str


# Circuit Block


class CircuitInactive(ProductBlockModel, product_block_name="Circuit"):
    """Object model for a Circuit as used by
    Backbone Link Service"""

    members: ListOfMembers[Layer3Interface]
    circuit_id: int
    admin_state: CircuitState


class CircuitProvisioning(CircuitInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    """Circuit with fields for use in the provisioning lifecycle"""

    members: ListOfMembers[Layer3Interface]
    circuit_id: int
    admin_state: CircuitState


class Circuit(CircuitProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """Circuit with fields for use in the active lifecycle"""

    members: ListOfMembers[Layer3Interface]
    circuit_id: int
    admin_state: CircuitState
