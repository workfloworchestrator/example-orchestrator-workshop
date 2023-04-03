from orchestrator.domain.base import SubscriptionModel
from orchestrator.types import SubscriptionLifecycle

from product_blocks.node import (
    NodeBlock,
    NodeInactiveBlock,
    NodeProvisioningBlock,
)

# In here, we define the values expected for a product block at each phase of the of the Subscription Lifecycle
# All resource types used by a product block need to be explicitly called out here and assigned
# expected types


class NodeInactive(SubscriptionModel, is_base=True):
    # Node state is planned
    node: NodeInactiveBlock


class NodeProvisioning(NodeInactiveBlock, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    # Node state is Commissioning
    node: NodeProvisioningBlock


class Node(NodeProvisioningBlock, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    # Node state is Provisioned
    node: NodeBlock
