# Copyright 2019-2022 SURF.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from collections.abc import Generator

from orchestrator.forms import FormPage
from orchestrator.forms.validators import ContactPersonList, Divider, Label, OrganisationId, MigrationSummary
from orchestrator.targets import Target
from orchestrator.types import FormGenerator, State, SubscriptionLifecycle, UUIDstr
from orchestrator.workflow import StepList, begin, step
from orchestrator.workflows.steps import store_process_subscription

from surf.forms.validators import JiraTicketId
from surf.products.product_types.circuit import CircuitInactive, CircuitProvisioning
from surf.products.services.subscription import subscription_description
from surf.workflows.shared.mail import send_confirmation_email
from surf.workflows.workflow import create_workflow



def initial_input_form_generator(product_name: str) -> FormGenerator:
    # TODO add additional fields to form if needed

    class CreateCircuitForm(FormPage):
        class Config:
            title = product_name

        organisation: OrganisationId
        contact_persons: ContactPersonList = []  # type: ignore
        ticket_id: JiraTicketId = JiraTicketId("")

        label_circuit_settings: Label
        divider_1: Divider

        members: list | None = None 
        circuit_id: int 
        under_maintenance: bool 
        

    user_input = yield CreateCircuitForm

    user_input_dict = user_input.dict()
    yield from create_summary_form(user_input_dict, product_name)

    return user_input_dict


def create_summary_form(
    user_input: dict,
    product_name: str,
) -> Generator:
    product_summary_fields = [ "members", "circuit_id", "under_maintenance",]

    class ProductSummary(MigrationSummary):
        data = {
            "labels": product_summary_fields,
            "columns": [[str(user_input[nm]) for nm in product_summary_fields]],
        }

    class SummaryForm(FormPage):
        class Config:
            title = f"{product_name} Summary"

        product_summary: ProductSummary
        divider_1: Divider

        # TODO fill in additional details if needed

    yield SummaryForm


@step("Construct Subscription model")
def construct_circuit_model(
    product: UUIDstr,
    organisation: UUIDstr,
    members: list | None,
    circuit_id: int,
    under_maintenance: bool,
    ) -> State:
    circuit = CircuitInactive.from_product_id(
        product_id=product,
        customer_id=organisation,
        status=SubscriptionLifecycle.INITIAL,
    )

    circuit.ckt.members = members
    circuit.ckt.circuit_id = circuit_id
    circuit.ckt.under_maintenance = under_maintenance
    

    circuit = CircuitProvisioning.from_other_lifecycle(circuit, SubscriptionLifecycle.PROVISIONING)
    circuit.description = subscription_description(circuit)

    return {
        "subscription": circuit,
        "subscription_id": circuit.subscription_id,  # necessary to be able to use older generic step functions
        "subscription_description": circuit.description,
    }


@create_workflow("Create Circuit", initial_input_form=initial_input_form_generator)
def create_circuit() -> StepList:
    return (
        begin
        >> construct_circuit_model
        >> store_process_subscription(Target.CREATE)
        # TODO add additional steps
        >> send_confirmation_email()
    )