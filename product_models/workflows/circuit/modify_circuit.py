from collections.abc import Generator

import structlog

from orchestrator.forms import FormPage, ReadOnlyField
from orchestrator.forms.validators import OrganisationId, contact_person_list, Divider
from orchestrator.types import FormGenerator, State, UUIDstr
from orchestrator.workflow import StepList, begin, step

from surf.forms.validators import JiraTicketId
from .circuit import Circuit, CircuitProvisioning
from surf.products.services.subscription import subscription_description
from surf.workflows.shared.mail import send_confirmation_email
from surf.workflows.shared.validate_subscriptions import subscription_update_wrapper
from surf.workflows.workflow import modify_workflow

from surf.workflows.circuit.shared.forms import circuit_id_must_be_unique_validator


logger = structlog.get_logger(__name__)


def initial_input_form_generator(subscription_id: UUIDstr) -> FormGenerator:
    subscription = Circuit.from_subscription(subscription_id)
    circuit = subscription.circuit

    # TODO fill in additional fields if needed

    class ModifyCircuitForm(FormPage):
        organisation: OrganisationId = subscription.customer_id  # type: ignore
        contact_persons: contact_person_list(subscription.customer_id) = []  # type:ignore
        ticket_id: JiraTicketId = JiraTicketId("")

        divider_1: Divider

        members: list | None = circuit.members
        circuit_id: int = circuit.circuit_id
        under_maintenance: bool = circuit.under_maintenance
        
        _validate_circuit_id_must_be_unique: classmethod = circuit_id_must_be_unique_validator()


    user_input = yield ModifyCircuitForm
    user_input_dict = user_input.dict()

    yield from create_summary_form(user_input_dict, subscription)

    return user_input_dict | {"subscription": subscription}


def create_summary_form(user_input: dict, subscription: Circuit) -> Generator:
    product_summary_fields = [ "members", "circuit_id", "under_maintenance",]

    before = [str(getattr(subscription.domain_settings, nm)) for nm in product_summary_fields]
    after = [str(user_input[nm]) for nm in product_summary_fields]

    class ProductSummary(MigrationSummary):
        data = {
            "labels": product_summary_fields,
            "headers": ["Before", "After"],
            "columns": [before, after],
        }

    class SummaryForm(FormPage):
        class Config:
            title = f"{subscription.product.name} Summary"

        product_summary: ProductSummary
        divider_1: Divider

    # TODO fill in additional details if needed

    yield SummaryForm


@step("Update subscription")
def update_subscription(
    subscription: CircuitProvisioning,
    members: list | None,
    circuit_id: int,
    under_maintenance: bool,
    ) -> State:
    # TODO: get all modified fields
    subscription.circuit.members = members
    subscription.circuit.circuit_id = circuit_id
    subscription.circuit.under_maintenance = under_maintenance
    return {"subscription": subscription}


@step("Update subscription description")
def update_subscription_description(subscription: Circuit) -> State:
    subscription.description = subscription_description(subscription)
    return {"subscription": subscription}


@modify_workflow("Modify Circuit", initial_input_form=initial_input_form_generator)
def modify_circuit() -> StepList:
    return (
        begin
        >> subscription_update_wrapper(update_subscription)
        >> update_subscription_description
        # TODO add additional steps if needed
        >> send_confirmation_email()
    )