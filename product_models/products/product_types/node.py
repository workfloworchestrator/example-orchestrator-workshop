
from orchestrator.domain.base import SubscriptionModel
from orchestrator.types import SubscriptionLifecycle

from products.product_blocks.node import (
    NodeBlock,
    NodeBlockInactive,
    NodeBlockProvisioning,
)



class NodeInactive(SubscriptionModel, is_base=True):
    node: NodeBlockInactive

class NodeProvisioning(NodeInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    node: NodeBlockProvisioning

class Node(NodeProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    node: NodeBlock