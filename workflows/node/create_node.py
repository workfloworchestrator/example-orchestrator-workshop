from typing import Any, Dict, List
import ipaddress

import structlog
from orchestrator.forms import FormPage
from orchestrator.forms.validators import Choice
from orchestrator.targets import Target
from orchestrator.types import FormGenerator, State, SubscriptionLifecycle, UUIDstr
from orchestrator.workflow import StepList, begin, step
from orchestrator.workflows.steps import set_status, store_process_subscription

from products.product_types.node import NodeInactive, NodeProvisioning, Node

from ..shared import CUSTOMER_UUID, create_workflow
from utils import netbox

logger = structlog.get_logger(__name__)


def get_nodes_list() -> List[Dict[str, Any]]:
    return netbox.dcim.get_devices()


def initial_input_form_generator(product_name: str) -> FormGenerator:
    nodes = get_nodes_list()
    choices = [node.get("name") for node in nodes]  # TODO: filter by node status
    NodeEnum = Choice("NodeEnum", zip(choices, choices))  # type: ignore

    class CreateNodeForm(FormPage):
        class Config:
            title = product_name

        select_node_choice: NodeEnum  # type: ignore

    user_input = yield CreateNodeForm
    node_data = next(
        node for node in nodes if user_input.select_node_choice == node["name"]
    )

    return {"node_id": node_data.get("id"), "node_name": node_data.get("name")}


@step("Construct Node model")
def construct_node_model(
    product: UUIDstr,
    node_id: int,
    node_name: str,
) -> State:
    subscription = NodeInactive.from_product_id(
        product_id=product,
        customer_id=CUSTOMER_UUID,
        status=SubscriptionLifecycle.INITIAL,
    )

    subscription.node.node_id = node_id
    subscription.node.node_name = node_name
    subscription.description = f"Node {node_name} Subscription"

    return {
        "subscription": subscription,
        "subscription_id": subscription.subscription_id,
    }


@step("Fetch Detailed IP information")
def fetch_ip_address_information(
    subscription: NodeInactive,
) -> State:
    detailed_node = netbox.dcim.get_devices(name=subscription.node.node_name)
    v4_network = ipaddress.ip_network(
        detailed_node[0].get("primary_ip4").get("address")
    )
    subscription.node.ipv4_loopback = v4_network.network_address
    v6_network = ipaddress.ip_network(
        detailed_node[0].get("primary_ip6").get("address")
    )
    subscription.node.ipv6_loopback = v6_network.network_address

    return {"subscription": subscription}


@step("Update Node Data in Netbox")
def update_node_status_netbox(
    subscription: NodeProvisioning,
) -> State:
    netbox_device = netbox.dcim.update_device(
        device_name=subscription.node.node_name,
        kwargs={"id": subscription.node.node_id, "status": "active"},
    )
    return {"netbox_device": netbox_device}


@step("POST node")
def add_device(subscription: NodeProvisioning) -> State:
    payload = {
        "id": subscription.node.node_id,
        "name": subscription.node.node_name,
        "v4_loopback": subscription.node.ipv4_loopback,
        "v6_loopback": subscription.node.ipv6_loopback,
    }
    # POST to wherever you would like this payload
    return {"payload": payload}


@create_workflow(
    "Create Node",
    initial_input_form=initial_input_form_generator,
    status=SubscriptionLifecycle.ACTIVE,
)
def create_node() -> StepList:
    return (
        begin
        >> construct_node_model
        >> store_process_subscription(Target.CREATE)
        >> fetch_ip_address_information
        >> set_status(SubscriptionLifecycle.PROVISIONING)
        >> add_device
        >> update_node_status_netbox
    )
