"""Workflow to initially create a circuit between two nodes."""
from typing import Any, List
import ipaddress

import structlog
from orchestrator.forms import FormPage, ReadOnlyField
from orchestrator.forms.validators import Choice, Accept, LongText
from orchestrator.targets import Target
from orchestrator.types import FormGenerator, State, SubscriptionLifecycle, UUIDstr
from orchestrator.workflow import StepList, begin, step, inputstep
from orchestrator.workflows.steps import set_status, store_process_subscription
from orchestrator.config.assignee import Assignee
from products.product_types.node import NodeInactive, NodeProvisioning
from utils import netbox

from ..shared import CUSTOMER_UUID, create_workflow


logger = structlog.get_logger(__name__)

def get_cables_list() -> List[Any]:
    pass

def initial_input_form_generator(product_name: str) -> FormGenerator:
    """
    Generates the Circuit Form to display to the user.
    """
    logger.info("Generating initial input form for Circuit")

    CircuitEnum = Choice("CircuitEnum", zip("test", "test"))
    class CreateCircuitForm(FormPage):
        """FormPage for Creating a node"""

        class Config:
            """Config class for Creating a node"""

            title = product_name

        select_node_choice: CircuitEnum  # type: ignore

    user_input = yield CreateCircuitForm


    return {"test": "test"}


@step("Construct Node model")
def construct_circuit_model(
    product: UUIDstr,
    node_id: int,
    node_name: str,
) -> State:
    pass

@step("Reserve IPs in Netbox")
def reserve_ips_in_ipam(
    subscription: NodeInactive,
) -> State:
    pass

@inputstep("Provide Config to User", assignee=Assignee.SYSTEM)
def provide_config_to_user(subscription: NodeProvisioning) -> FormGenerator:
    pass

@step("Update Circuit Status in Netbox")
def update_circuit_status_netbox(
    subscription: NodeProvisioning,
) -> State:
    pass

@create_workflow(
    "Create Circuit",
    initial_input_form=initial_input_form_generator,
    status=SubscriptionLifecycle.ACTIVE,
)
def create_circuit() -> StepList:
    """Workflow steplist"""
    return (
        begin
        >> construct_circuit_model
        >> store_process_subscription(Target.CREATE)
        >> reserve_ips_in_ipam
        >> provide_config_to_user
        >> set_status(SubscriptionLifecycle.PROVISIONING)
        >> update_circuit_status_netbox
    )
