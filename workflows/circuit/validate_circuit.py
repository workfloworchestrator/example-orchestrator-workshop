from orchestrator.types import State, UUIDstr
from orchestrator.workflow import StepList, begin, step
from orchestrator.workflows.utils import validate_workflow

from products.product_types.circuit import Circuit
from workflows.shared import is_active


@step("Load relevant Circuit subscription information")
def load_node_subscription_info(subscription_id: UUIDstr) -> State:
    subscription = Circuit.from_subscription(subscription_id)

    return {
        "subscription": subscription,
    }


@validate_workflow("Validate Circuit")
def validate_circuit() -> StepList:
    return begin >> load_node_subscription_info >> is_active()
