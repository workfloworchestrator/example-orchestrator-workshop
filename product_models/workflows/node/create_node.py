from collections.abc import Generator

from orchestrator.forms import FormPage
from orchestrator.forms.validators import ContactPersonList, Divider, Label, OrganisationId, MigrationSummary
from orchestrator.targets import Target
from orchestrator.types import FormGenerator, State, SubscriptionLifecycle, UUIDstr
from orchestrator.workflow import StepList, begin, step
from orchestrator.workflows.steps import store_process_subscription

from surf.forms.validators import JiraTicketId
from .node import NodeInactive, NodeProvisioning
from surf.products.services.subscription import subscription_description
from surf.workflows.shared.mail import send_confirmation_email
from surf.workflows.workflow import create_workflow



def initial_input_form_generator(product_name: str) -> FormGenerator:
    # TODO add additional fields to form if needed

    class CreateNodeForm(FormPage):
        class Config:
            title = product_name

        organisation: OrganisationId
        contact_persons: ContactPersonList = []  # type: ignore
        ticket_id: JiraTicketId = JiraTicketId("")

        label_node_settings: Label
        divider_1: Divider

        node_id: int 
        node_name: str 
        ipv4_loopback: ipaddress.IPv4Address 
        ipv6_loopback: ipaddress.IPv6Address 
        

    user_input = yield CreateNodeForm

    user_input_dict = user_input.dict()
    yield from create_summary_form(user_input_dict, product_name)

    return user_input_dict


def create_summary_form(
    user_input: dict,
    product_name: str,
) -> Generator:
    product_summary_fields = [ "node_id", "node_name", "ipv4_loopback", "ipv6_loopback",]

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
def construct_node_model(
    product: UUIDstr,
    organisation: UUIDstr,
    node_id: int,
    node_name: str,
    ipv4_loopback: ipaddress.IPv4Address,
    ipv6_loopback: ipaddress.IPv6Address,
    ) -> State:
    node = NodeInactive.from_product_id(
        product_id=product,
        customer_id=organisation,
        status=SubscriptionLifecycle.INITIAL,
    )

    node.node.node_id = node_id
    node.node.node_name = node_name
    node.node.ipv4_loopback = ipv4_loopback
    node.node.ipv6_loopback = ipv6_loopback
    

    node = NodeProvisioning.from_other_lifecycle(node, SubscriptionLifecycle.PROVISIONING)
    node.description = subscription_description(node)

    return {
        "subscription": node,
        "subscription_id": node.subscription_id,  # necessary to be able to use older generic step functions
        "subscription_description": node.description,
    }


@create_workflow("Create node", initial_input_form=initial_input_form_generator)
def create_node() -> StepList:
    return (
        begin
        >> construct_node_model
        >> store_process_subscription(Target.CREATE)
        # TODO add additional steps
        >> send_confirmation_email()
    )