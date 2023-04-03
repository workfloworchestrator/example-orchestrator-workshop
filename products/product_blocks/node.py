from typing import Optional
from uuid import UUID

from orchestrator.domain.base import ProductBlockModel
from orchestrator.types import SubscriptionLifecycle

# In here, we define the values expected for a product block at each phase of the of the Subscription Lifecycle
# All resource types used by a product block need to be explicitly called out here and assigned
# expected types


class NodeInactiveBlock(ProductBlockModel, product_block_name="Node"):
    """Object model for a Node as used by Node Service"""

    # when first created we expect all resources to be none
    node_id: Optional[int] = None
    node_name: Optional[str] = None
    ipv4_ipam_id: Optional[UUID] = None
    ipv6_ipam_id: Optional[str] = None


class NodeProvisioningBlock(NodeInactiveBlock, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    """Node Enrollment with optional fields to use in the provisioning lifecycle state."""

    # In the Provisioning state, there will be an ESDB node, Device Group, and NSO service assigned
    node_id: int
    node_name: str
    ipv4_ipam_id: UUID
    ipv6_ipam_id: str


class NodeBlock(NodeProvisioningBlock, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """Node  with optional fields to use in the active lifecycle state."""

    # In the active state, there will be an ESDB node, Device Group, and NSO service assigned
    node_id: int
    esdb_node_uuid: UUID
    node_name: str
    ipv4_ipam_id: UUID
    ipv6_ipam_id: str
