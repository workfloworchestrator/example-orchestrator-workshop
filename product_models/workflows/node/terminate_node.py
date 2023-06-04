
from orchestrator.types import State, UUIDstr
from orchestrator.workflow import StepList, begin, step

from products.product_types.node import Node

from surf.workflows.workflow import terminate_initial_input_form_generator, terminate_workflow


@step("Load initial state")
def load_initial_state(subscription: Node) -> State:
    # TODO: optionally add additional values.
    # Copy values to the root of the state for easy access

    return {
        "subscription": subscription,
    }



@terminate_workflow("Terminate node", initial_input_form=terminate_initial_input_form_generator)
def terminate_node() -> StepList:
    return (
        begin
        >> load_initial_state
        # TODO: fill in additional steps if needed
    )