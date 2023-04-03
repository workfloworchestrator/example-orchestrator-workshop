from orchestrator.domain.base import SubscriptionModel
from orchestrator.types import SubscriptionLifecycle

from product_blocks.node import (
    Node,
    NodeInactive,
    NodeProvisioning,
)

# In here, we define the values expected for a product block at each phase of the of the Subscription Lifecycle
# All resource types used by a product block need to be explicitly called out here and assigned
# expected types


class NodeInactive(SubscriptionModel, is_base=True):
    # Equipment state is planned
    ne: NodeInactive


class NodeProvisioning(NodeInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    # Equipment state is Commissioning
    ne: NodeProvisioning


class NodeEnrollment(NodeProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    # Equipment state is Provisioned
    ne: Node
