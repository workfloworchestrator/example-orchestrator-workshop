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

import structlog

from orchestrator.forms import FormPage, ReadOnlyField
from orchestrator.forms.validators import OrganisationId, contact_person_list, Divider
from orchestrator.types import FormGenerator, State, UUIDstr
from orchestrator.workflow import StepList, begin, step

from surf.forms.validators import JiraTicketId
from surf.products.product_types.ws_node import node, nodeProvisioning
from surf.products.services.subscription import subscription_description
from surf.workflows.shared.mail import send_confirmation_email
from surf.workflows.shared.validate_subscriptions import subscription_update_wrapper
from surf.workflows.workflow import modify_workflow


logger = structlog.get_logger(__name__)


def initial_input_form_generator(subscription_id: UUIDstr) -> FormGenerator:
    subscription = node.from_subscription(subscription_id)
    node = subscription.node

    # TODO fill in additional fields if needed

    class ModifynodeForm(FormPage):
        organisation: OrganisationId = subscription.customer_id  # type: ignore
        contact_persons: contact_person_list(subscription.customer_id) = []  # type:ignore
        ticket_id: JiraTicketId = JiraTicketId("")

        divider_1: Divider

        node_id: int = node.node_id
        node_name: str = node.node_name
        ipv4_loopback: ipaddress.IPv4Address = node.ipv4_loopback
        ipv6_loopback: ipaddress.IPv6Address = node.ipv6_loopback
        

    user_input = yield ModifynodeForm
    user_input_dict = user_input.dict()

    yield from create_summary_form(user_input_dict, subscription)

    return user_input_dict | {"subscription": subscription}


def create_summary_form(user_input: dict, subscription: node) -> Generator:
    product_summary_fields = [ "node_id", "node_name", "ipv4_loopback", "ipv6_loopback",]

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
    subscription: nodeProvisioning,
    node_id: int,
    node_name: str,
    ipv4_loopback: ipaddress.IPv4Address,
    ipv6_loopback: ipaddress.IPv6Address,
    ) -> State:
    # TODO: get all modified fields
    subscription.node.node_id = node_id
    subscription.node.node_name = node_name
    subscription.node.ipv4_loopback = ipv4_loopback
    subscription.node.ipv6_loopback = ipv6_loopback
    return {"subscription": subscription}


@step("Update subscription description")
def update_subscription_description(subscription: node) -> State:
    subscription.description = subscription_description(subscription)
    return {"subscription": subscription}


@modify_workflow("Modify Node", initial_input_form=initial_input_form_generator)
def modify_ws_node() -> StepList:
    return (
        begin
        >> subscription_update_wrapper(update_subscription)
        >> update_subscription_description
        # TODO add additional steps if needed
        >> send_confirmation_email()
    )