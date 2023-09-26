from ipaddress import IPv4Network, IPv6Network
from typing import Optional

from orchestrator.domain.base import ProductBlockModel
from orchestrator.types import SubscriptionLifecycle

# In here, we define the values expected for a product block at each phase of the of the Subscription Lifecycle
# All resource types used by a product block need to be explicitly called out here and assigned
# expected types


class NodeBlockInactive(ProductBlockModel, product_block_name="Node"):
    """Object model for a Node as used by Node Service"""

    # when first created we expect all resources to be none
    node_id: Optional[int] = None
    node_name: Optional[str] = None
    node_status: Optional[str] = None
    ipv4_loopback: Optional[IPv4Network] = None
    ipv6_loopback: Optional[IPv6Network] = None


class NodeBlockProvisioning(NodeBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    """Node Enrollment with optional fields to use in the provisioning lifecycle state."""

    node_id: int
    node_name: str
    node_status: str
    ipv4_loopback: IPv4Network
    ipv6_loopback: IPv6Network


class NodeBlock(NodeBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """Node  with optional fields to use in the active lifecycle state."""

    node_id: int
    node_name: str
    node_status: str
    ipv4_loopback: IPv4Network
    ipv6_loopback: IPv6Network
