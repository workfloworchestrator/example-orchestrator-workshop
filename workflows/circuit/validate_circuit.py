from orchestrator.types import State, UUIDstr
from orchestrator.workflow import step, StepList, begin
from orchestrator.workflows.utils import validate_workflow
from workflows.shared import is_active
from products.product_types.circuit import Circuit


@step("Load relevant Circuit subscription information")
def load_node_subscription_info(subscription_id: UUIDstr) -> State:
    subscription = Circuit.from_subscription(subscription_id)

    return {
        "subscription": subscription,
    }


@validate_workflow("Validate Circuit")
def validate_circuit() -> StepList:
    return begin >> load_node_subscription_info >> is_active()
