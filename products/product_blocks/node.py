from typing import Optional
from uuid import UUID

from orchestrator.domain.base import ProductBlockModel
from orchestrator.types import SubscriptionLifecycle

# In here, we define the values expected for a product block at each phase of the of the Subscription Lifecycle
# All resource types used by a product block need to be explicitly called out here and assigned
# expected types


class NodeInactive(ProductBlockModel, product_block_name="Node Enrollment"):
    """Object model for a Node Enrollment as used by Node Enrollment Service"""

    # when first created we expect all resources to be none
    node_id: Optional[int] = None
    node_name: Optional[str] = None
    nso_service_id: Optional[UUID] = None
    v6_loopback: Optional[str] = None


class NodeProvisioning(NodeInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    """Node Enrollment with optional fields to use in the provisioning lifecycle state."""

    # In the Provisioning state, there will be an ESDB node, Device Group, and NSO service assigned
    node_id: int
    node_name: str
    nso_service_id: UUID
    v6_loopback: str


class Node(NodeProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    """Node  with optional fields to use in the active lifecycle state."""

    # In the active state, there will be an ESDB node, Device Group, and NSO service assigned
    node_id: int
    esdb_node_uuid: UUID
    node_name: str
    nso_service_id: UUID
    v6_loopback: str
