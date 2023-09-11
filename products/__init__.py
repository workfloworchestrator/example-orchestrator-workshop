from orchestrator.domain import SUBSCRIPTION_MODEL_REGISTRY

from products.product_types.circuit import Circuit
from products.product_types.node import Node

SUBSCRIPTION_MODEL_REGISTRY.update({"Node": Node, "Circuit": Circuit})  # type: ignore
