from typing import TypeVar, Optional
from uuid import UUID

from orchestrator.domain.base import ProductBlockModel, SubscriptionInstanceList
from orchestrator.types import SubscriptionLifecycle
from orchestrator.forms.validators import Choice
from products.product_blocks.node import (
    NodeBlock,
    NodeBlockInactive,
    NodeBlockProvisioning,
)

# Product Block definitions for Circuit Service

# Constrained lists for models

T = TypeVar("T", covariant=True)


class PortPair(SubscriptionInstanceList[T]):
    min_items = 2
    max_items = 2


class CircuitState(Choice):
    UP = "up"
    DOWN = "down"


# Port


class PortInactive(ProductBlockModel, product_block_name="Port"):
    """Object model for a Port as used by
    Circuit Service"""

    port_id: Optional[int]
    port_description: Optional[str]
    node: NodeBlockInactive


class PortProvisioning(PortInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    """Port with fields for use in the provisioning lifecycle"""

    port_id: int
    port_description: str
    node: NodeBlockProvisioning


class Port(PortProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """Port with fields for use in the provisioning lifecycle"""

    port_id: int
    port_description: str
    node: NodeBlock


# Layer 3 Interface


class Layer3InterfaceInactive(
    ProductBlockModel, product_block_name="Layer 3 Interface"
):
    """Object model for a Layer 3 Interface as used by Circuit"""

    port: PortInactive
    v6_ip_address: Optional[str]


class Layer3InterfaceProvisioning(
    Layer3InterfaceInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """Layer 3 Interface with fields for use in the provisioning lifecycle"""

    port: PortProvisioning
    v6_ip_address: str


class Layer3Interface(
    Layer3InterfaceProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    """Layer 3 Interface with fields for use in the active lifecycle"""

    port: Port
    v6_ip_address: str


# Circuit Block


class CircuitBlockInactive(ProductBlockModel, product_block_name="Circuit"):
    """Object model for a Circuit as used by
    Backbone Link Service"""

    members: PortPair[Layer3InterfaceInactive]
    circuit_id: Optional[int]
    admin_state: Optional[CircuitState]


class CircuitBlockProvisioning(
    CircuitBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    """Circuit with fields for use in the provisioning lifecycle"""

    members: PortPair[Layer3InterfaceProvisioning]
    circuit_id: int
    admin_state: CircuitState


class CircuitBlock(CircuitBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """Circuit with fields for use in the active lifecycle"""

    members: PortPair[Layer3Interface]
    circuit_id: int
    admin_state: CircuitState
