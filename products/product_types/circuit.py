from orchestrator.domain.base import SubscriptionModel
from orchestrator.types import SubscriptionLifecycle

from products.product_blocks.circuit import (
    CircuitBlock,
    CircuitBlockInactive,
    CircuitBlockProvisioning,
)

# In here, we define the values expected for a product block at each phase of the of the Subscription Lifecycle
# All resource types used by a product block need to be explicitly called out here and assigned
# expected types


class CircuitInactive(SubscriptionModel, is_base=True):
    # Equipment state is planned
    # speed = fixed input & is string
    speed: str
    ckt: CircuitBlockInactive
    
    
class CircuitProvisioning(CircuitInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    # speed = fixed input & is string
    speed: str
    ckt: CircuitBlockProvisioning
    
    
class Circuit(CircuitProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    # speed = fixed input & is string
    speed: str
    ckt: CircuitBlock
