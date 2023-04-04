from typing import Any, Dict, List

import structlog
from orchestrator.forms import FormPage
from orchestrator.forms.validators import Choice
from orchestrator.targets import Target
from orchestrator.types import FormGenerator, State, SubscriptionLifecycle, UUIDstr
from orchestrator.workflow import StepList, begin, step
from orchestrator.workflows.steps import store_process_subscription
from pydantic import validator

from products.product_types.node import NodeInactive

from ..shared import CUSTOMER_UUID, create_workflow
from utils import netbox

logger = structlog.get_logger(__name__)


def validate_node(node_name: str) -> str:
    # TODO: demonstrate simple node validation
    pass


def get_nodes_list() -> List[Dict[str, Any]]:
    return netbox.dcim.get_devices()


def initial_input_form_generator(product_name: str) -> FormGenerator:
    nodes = get_nodes_list()
    choices = [node["name"] for node in nodes]
    NodeEnum = Choice("NodeEnum", zip(choices, choices))  # type: ignore

    class CreateNodeForm(FormPage):
        class Config:
            title = product_name

        select_node_choice: NodeEnum  # type: ignore
        validate_node = validator("select_node_choice", allow_reuse=True)(validate_node)

    user_input = yield CreateNodeForm
    node_data = next(
        node for node in nodes if user_input.select_node_choice == node["name"]
    )

    return {
        "node_data": node_data,
    }


@step("Construct Node model")
def construct_node_model(
    product: UUIDstr,
    node_data: Dict[str, Any],
) -> State:
    subscription = NodeInactive.from_product_id(
        product_id=product,
        customer_id=CUSTOMER_UUID,
        status=SubscriptionLifecycle.INITIAL,
    )

    subscription.node.node_id = node_data["id"]
    subscription.node.node_name = node_data["name"]
    subscription.description = f"Node {node_data['name']} Subscription"

    return {
        "subscription": subscription,
    }


@step("POST node")
def add_device() -> State:
    pass


@create_workflow(
    "Enroll Core Router",
    initial_input_form=initial_input_form_generator,
)
def create_node_enrollment() -> StepList:
    return (
        begin
        >> construct_node_model
        >> store_process_subscription(Target.CREATE)
        >> add_device
    )
