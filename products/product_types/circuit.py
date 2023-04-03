from orchestrator.domain.base import SubscriptionModel
from orchestrator.types import SubscriptionLifecycle

from product_blocks.circuit import (
    Circuit,
    CircuitInactive,
    CircuitProvisioning,
)

# In here, we define the values expected for a product block at each phase of the of the Subscription Lifecycle
# All resource types used by a product block need to be explicitly called out here and assigned
# expected types


class CircuitInactive(SubscriptionModel, is_base=True):
    # Equipment state is planned
    # speed = fixed input & is string
    speed: str
    ckt: CircuitInactive
    
    
class CircuitProvisioning(CircuitInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    # Equipment state is Commissioning
    # speed = fixed input & is string
    speed: str
    ckt: CircuitProvisioning
    
    
class Circuit(CircuitProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    # Equipment state is Provisioned
    # speed = fixed input & is string
    speed: str
    ckt: Circuit
