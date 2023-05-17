from orchestrator.domain.base import SubscriptionModel
from orchestrator.types import strEnum, SubscriptionLifecycle

from products.product_blocks.circuit import (
    CircuitBlock,
    CircuitBlockInactive,
    CircuitBlockProvisioning,
)

# In here, we define the values expected for a product block at each phase of the of the Subscription Lifecycle
# All resource types used by a product block need to be explicitly called out here and assigned
# expected types


class Speed(strEnum):
    HUNDREDG = "100G"


class CircuitInactive(SubscriptionModel, is_base=True):
    # Equipment state is planned
    speed: Speed
    circuit: CircuitBlockInactive


class CircuitProvisioning(
    CircuitInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    speed: Speed
    circuit: CircuitBlockProvisioning


class Circuit(CircuitProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    speed: Speed
    circuit: CircuitBlock
