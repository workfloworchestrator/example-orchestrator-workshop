from orchestrator.domain import SUBSCRIPTION_MODEL_REGISTRY
from products.product_types.node import Node
from products.product_types.circuit import Circuit
SUBSCRIPTION_MODEL_REGISTRY.update({
    "Node": Node, # type: ignore
    "Circuit": Circuit
})
