"""Workflow to initially provision a node."""
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

from workflows.shared import CUSTOMER_UUID, create_workflow


logger = structlog.get_logger(__name__)


def get_nodes_list() -> List[Any]:
    """
    Connects to netbox and returns a list of netbox device objects.
    """
    logger.debug("Connecting to Netbox to get list of available nodes")
    node_list = list(netbox.dcim.devices.filter(status="planned"))
    logger.debug("Found nodes in Netbox", amount=len(node_list))
    return node_list


def initial_input_form_generator(product_name: str) -> FormGenerator:
    """
    Generates the Node Form to display to the user.
    """
    logger.debug("Generating initial input form")
    nodes = get_nodes_list()
    choices = [node.name for node in nodes]
    NodeEnum = Choice("Planned nodes", zip(choices, choices))  # type: ignore

    class CreateNodeForm(FormPage):
        """FormPage for Creating a node"""

        class Config:
            """Config class for Creating a node"""

            title = product_name

        select_node_choice: NodeEnum  # type: ignore

    user_input = yield CreateNodeForm
    node_data = next(
        node for node in nodes if user_input.select_node_choice == node.name
    )

    return {"node_id": node_data.id, "node_name": node_data.name}


@step("Construct Node model")
def construct_node_model(
    product: UUIDstr,
    node_id: int,
    node_name: str,
) -> State:
    """Creates the node model in it's initial state."""
    logger.debug("Constructing Node model for node", node_name=node_name)
    subscription = NodeInactive.from_product_id(
        product_id=product,
        customer_id=CUSTOMER_UUID,
        status=SubscriptionLifecycle.INITIAL,
    )

    subscription.node.node_id = node_id
    subscription.node.node_name = node_name
    subscription.description = f"Node {node_name}"

    return {
        "subscription": subscription,
        "subscription_id": subscription.subscription_id,
    }


@step("Fetch Detailed IP information")
def fetch_ip_address_information(
    subscription: NodeInactive,
) -> State:
    """Grabs the IP address information for the node and puts it on the domain model."""
    logger.debug(
        "Fetching detailed IP information for node from netbox",
        node_name=subscription.node.node_name,
    )
    detailed_node = netbox.dcim.devices.get(name=subscription.node.node_name)
    v4_network = ipaddress.ip_network(detailed_node.primary_ip4.address)
    subscription.node.ipv4_loopback = ipaddress.IPv4Address(v4_network.network_address)
    v6_network = ipaddress.ip_network(detailed_node.primary_ip6.address)
    subscription.node.ipv6_loopback = ipaddress.IPv6Address(v6_network.network_address)

    return {"subscription": subscription}


@inputstep("Provide Config to User", assignee=Assignee.SYSTEM)
def provide_config_to_user(subscription: NodeProvisioning) -> FormGenerator:
    """Generates a configuration payload that a user can paste into a router."""
    logger.debug("Creating node payload", node_name=subscription.node.node_name)
    router_config = f"""! Paste the following config into {subscription.node.node_name}:
! to complete configuring the device
!
enable
configure terminal
!
hostname {subscription.node.node_name}
!
interface loopback 0
!
ip address {subscription.node.ipv4_loopback} 255.255.255.55
ipv6 address {subscription.node.ipv6_loopback}/128
!
exit
!
end
copy running-config startup-config"""

    class ConfigResults(FormPage):
        """FormPage for showing a user the config needed for a node"""

        node_config: LongText = ReadOnlyField(router_config)
        confirm_config_put_on_routers: Accept = Accept("INCOMPLETE")

    form_data = yield ConfigResults
    user_input = form_data.dict()
    return user_input


@step("Update Node Data in Netbox")
def update_node_status_netbox(
    subscription: NodeProvisioning,
) -> State:
    """Updates a node in netbox to be Active"""
    logger.debug(
        "Updating Node status in netbox", node_name=subscription.node.node_name
    )
    device = netbox.dcim.devices.get(name=subscription.node.node_name)
    device.status = "active"
    if not device.save():
        raise RuntimeError(f"Could not save device status {device.__dict__}")
    return {"netbox_device": device.name}


@create_workflow(
    "Create Node",
    initial_input_form=initial_input_form_generator,
    status=SubscriptionLifecycle.ACTIVE,
)
def create_node() -> StepList:
    """Workflow steplist"""
    return (
        begin
        >> construct_node_model
        >> store_process_subscription(Target.CREATE)
        >> fetch_ip_address_information
        >> provide_config_to_user
        >> set_status(SubscriptionLifecycle.PROVISIONING)
        >> update_node_status_netbox
    )
