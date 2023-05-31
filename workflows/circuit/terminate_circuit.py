from orchestrator import step
from orchestrator.types import State
from orchestrator.workflow import StepList, begin
from structlog import get_logger

from products import Circuit
from workflows.shared import terminate_workflow

logger = get_logger(__name__)


@step("Remove circuit")
def remove_circuit(subscription: Circuit) -> State:
    # Remove the circuit from netbox
    return {}


@terminate_workflow("Terminate the circuit")
def terminate_circuit() -> StepList:
    return begin >> remove_circuit
