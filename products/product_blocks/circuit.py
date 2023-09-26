from ipaddress import IPv6Interface
from typing import Optional, TypeVar

from orchestrator.domain.base import ProductBlockModel, SubscriptionInstanceList
from orchestrator.types import SubscriptionLifecycle

from products.product_blocks.node import NodeBlock

# Product Block definitions for Circuit Service

T = TypeVar("T", covariant=True)


class PortPair(SubscriptionInstanceList[T]):
    min_items = 2
    max_items = 2


# Port


class PortInactive(ProductBlockModel, product_block_name="Port"):
    """Object model for a Port as used by
    Circuit Service"""

    port_id: Optional[int] = None
    port_description: Optional[str] = None
    port_name: Optional[str] = None
    node: Optional[NodeBlock] = None


class PortProvisioning(PortInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    """Port with fields for use in the provisioning lifecycle"""

    port_id: int
    port_description: str
    port_name: str
    node: NodeBlock


class Port(PortProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """Port with fields for use in the provisioning lifecycle"""

    port_id: int
    port_description: str
    port_name: str
    node: NodeBlock


# Layer 3 Interface
class Layer3InterfaceInactive(ProductBlockModel, product_block_name="Layer 3 Interface"):
    """Object model for a Layer 3 Interface as used by Circuit"""

    port: PortInactive
    v6_ip_address: Optional[IPv6Interface] = None


class Layer3InterfaceProvisioning(Layer3InterfaceInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    """Layer 3 Interface with fields for use in the provisioning lifecycle"""

    port: PortProvisioning
    v6_ip_address: IPv6Interface


class Layer3Interface(Layer3InterfaceProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """Layer 3 Interface with fields for use in the active lifecycle"""

    port: Port
    v6_ip_address: IPv6Interface


# Circuit Block
class CircuitBlockInactive(ProductBlockModel, product_block_name="Circuit"):
    """Object model for a Circuit as used by
    Backbone Link Service"""

    members: PortPair[Layer3InterfaceInactive]
    circuit_id: Optional[int] = None
    circuit_status: Optional[str] = None
    circuit_description: Optional[str] = None
    under_maintenance: Optional[bool] = None


class CircuitBlockProvisioning(CircuitBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    """Circuit with fields for use in the provisioning lifecycle"""

    members: PortPair[Layer3InterfaceProvisioning]
    circuit_id: Optional[int] = None
    circuit_status: str
    circuit_description: str
    under_maintenance: bool


class CircuitBlock(CircuitBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """Circuit with fields for use in the active lifecycle"""

    members: PortPair[Layer3Interface]
    circuit_id: int
    circuit_status: str
    circuit_description: str
    under_maintenance: bool
