import structlog

from orchestrator.types import State
from orchestrator.workflow import StepList, begin, step
from orchestrator.workflows.utils import validate_workflow

from products.product_types.circuit import Circuit

from surf.workflows.shared.crm import load_organisation_info

logger = structlog.get_logger(__name__)


@step("Load initial state")
def load_initial_state_circuit(subscription: Circuit) -> State:
    return {
        "subscription": subscription,
    }



@validate_workflow("Validate Circuit")
def validate_circuit() -> StepList:
    return (
        begin
        >> load_initial_state_circuit
        >> load_organisation_info
    )