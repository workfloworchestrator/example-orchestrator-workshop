
from enum import IntEnum

from orchestrator.domain.base import SubscriptionModel
from orchestrator.types import SubscriptionLifecycle

from products.product_blocks.circuit import (
    CircuitBlock,
    CircuitBlockInactive,
    CircuitBlockProvisioning,
)

class Speed(IntEnum):
    ONEGIG = 1
    TENGIG = 10
    ONEHUDREDGIG = 100


class CircuitInactive(SubscriptionModel, is_base=True):
    speed: Speed
    circuit: CircuitBlockInactive

class CircuitProvisioning(CircuitInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    speed: Speed
    circuit: CircuitBlockProvisioning

class Circuit(CircuitProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    speed: Speed
    circuit: CircuitBlock