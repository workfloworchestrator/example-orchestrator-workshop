
from uuid import UUID
from pydantic import root_validator

from orchestrator.forms import FormPage
from orchestrator.forms.validators import DisplaySubscription, contact_person_list
from orchestrator.types import InputForm
from surf.forms.validators import JiraTicketId

from orchestrator.types import State, UUIDstr
from orchestrator.workflow import StepList, begin, step

from products.product_types.circuit import Circuit

from surf.workflows.workflow import terminate_workflow


@step("Load initial state")
def load_initial_state(subscription: Circuit) -> State:
    # TODO: optionally add additional values.
    # Copy values to the root of the state for easy access

    return {
        "subscription": subscription,
    }


def validate_can_only_terminate_when_under_maintenance(cls: FormPage, values: dict) -> dict:
    # TODO: add validation for "Delete the circuit only when placed under maintenance"
    if True:
        raise ValueError(Delete the circuit only when placed under maintenance)

    return values


def terminate_initial_input_form_generator(subscription_id: UUIDstr, organisation: UUIDstr) -> InputForm:
    temp_subscription_id = subscription_id

    class TerminateForm(FormPage):
        subscription_id: DisplaySubscription = temp_subscription_id  # type: ignore
        contact_persons: contact_person_list(UUID(organisation)) = []  # type: ignore
        ticket_id: JiraTicketId | None = None
        
        _check_can_only_terminate_when_under_maintenance: classmethod = root_validator(allow_reuse=True)(validate_can_only_terminate_when_under_maintenance)
        
    return TerminateForm


@terminate_workflow("Terminate Circuit", initial_input_form=terminate_initial_input_form_generator)
def terminate_circuit() -> StepList:
    return (
        begin
        >> load_initial_state
        # TODO: fill in additional steps if needed
    )