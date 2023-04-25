"""Workflow to initially create a circuit between two nodes."""
from ipaddress import IPv6Interface
from typing import Any, Generator, List

import structlog
from orchestrator.config.assignee import Assignee
from orchestrator.forms import FormPage, ReadOnlyField
from orchestrator.forms.validators import Accept, Choice, LongText
from orchestrator.services.subscriptions import (
    retrieve_subscription_by_subscription_instance_value,
)
from orchestrator.targets import Target
from orchestrator.types import FormGenerator, State, SubscriptionLifecycle, UUIDstr
from orchestrator.workflow import StepList, begin, inputstep, step
from orchestrator.workflows.steps import set_status, store_process_subscription

from products.product_types.circuit import CircuitInactive, CircuitProvisioning
from products.product_types.node import Node
from utils import netbox

from ..shared import CUSTOMER_UUID, create_workflow

logger = structlog.get_logger(__name__)

# The ID of the Subnet Block we will use for assigning IPs to circuits
CIRCUIT_PREFIX_IPAM_ID = 3
ISIS_AREA_ID = "49.0001.0123.4567.890a.0001.00"


def get_valid_cables_list() -> List[Any]:
    """
    Connects to netbox and returns a list of valid netbox circuits/cables.
    """
    logger.info("Connecting to Netbox to get list of available circuits/cables")
    valid_circuits = list(netbox.dcim.cables.filter(status="planned"))
    logger.info(f"Found {len(valid_circuits)} circuits/cables in Netbox")
    return valid_circuits


def format_circuits(circuit_list: List[Any]) -> Generator:
    """Formats a list of netbox circuits for display in the frontend"""
    pretty_circuits = []
    for circuit in circuit_list:
        if circuit.full_details():
            a_side = circuit.a_terminations[0]
            b_side = circuit.b_terminations[0]
            pretty_circuit = f"Circuit ID {circuit.id}: {a_side.device}:{a_side.name} <--> {b_side.device}:{b_side.name}"
            pretty_circuits.append(pretty_circuit)

            yield (circuit, pretty_circuit)
        else:
            raise ValueError("Could not pull full details of circuit")


def initial_input_form_generator(product_name: str) -> FormGenerator:
    """
    Generates the Circuit Form to display to the user.
    """
    logger.info("Generating initial input form for Circuit")
    # TODO: Add validator to make sure that the nodes this circuit depends on already exist.

    # First, get the data we need to present a list of circuits to a user
    valid_circuits = get_valid_cables_list()
    pretty_circuits = list(format_circuits(valid_circuits))

    # Then format the circuits into a choice list:
    choices = [circuit[1] for circuit in pretty_circuits]
    CircuitEnum = Choice("CircuitEnum", zip(choices, choices))

    # Next, construct the form to display to the user:
    class CreateCircuitForm(FormPage):
        """FormPage for Creating a Circuit"""

        class Config:
            """Config class for Creating a Circuit"""

            title = product_name

        select_circuit_choice: CircuitEnum  # type: ignore

    # Now we present the form to the user
    logger.info("Presenting CreateCircuitForm to user")
    user_input = yield CreateCircuitForm

    # Once we get the form selecton back from the user we send that circuit ID
    # to the state object for use in generating the subscription
    logger.info(f"User selected circuit/cable {user_input.select_circuit_choice}")
    circuit_data = next(
        circuit[0]
        for circuit in pretty_circuits
        if user_input.select_circuit_choice == circuit[1]
    )

    logger.info("Done with CreateCircuitForm")

    return {
        "circuit_id": circuit_data.id,
        "pretty_circuit": user_input.select_circuit_choice,
    }


@step("Construct Circuit model")
def construct_circuit_model(
    product: UUIDstr,
    state: State,
) -> State:
    """
    Construct the initial domain model for circuit
    """
    logger.info("Building initial circuit model")

    # First, we instantiate an empty subscription for a circuit subscription:
    subscription = CircuitInactive.from_product_id(
        product_id=product,
        customer_id=CUSTOMER_UUID,
        status=SubscriptionLifecycle.INITIAL,
    )

    # Next, we add the circuit details to the subscription
    logger.info("Adding Base Circuit Model fields to Subscription")
    subscription.ckt.circuit_id = state.get("circuit_id")
    subscription.ckt.under_maintenance = True

    # Then, we pull in the full details of this circuit from netbox for use later on:
    logger.info(
        f"Getting circuit details for Circuit {subscription.ckt.circuit_id} from NetBox"
    )
    netbox_circuit = netbox.dcim.cables.get(subscription.ckt.circuit_id)
    netbox_circuit.full_details()
    logger.info(
        f"Grabbing Device IDs for circuit {subscription.ckt.circuit_id} from NetBox"
    )

    node_a_netbox_id = str(netbox_circuit.a_terminations[0].device.id)
    node_b_netbox_id = str(netbox_circuit.b_terminations[0].device.id)

    logger.info("Linking existing node subscriptions")
    # Now, we get the existing node subscriptions from the DB:

    node_a_subscription = retrieve_subscription_by_subscription_instance_value(
        resource_type="node_id", value=node_a_netbox_id
    )
    node_b_subscription = retrieve_subscription_by_subscription_instance_value(
        resource_type="node_id", value=node_b_netbox_id
    )
    # Link the existing node subscriptions from the DB to the circuit subscription:
    subscription.ckt.members[0].port.node = Node.from_subscription(
        node_a_subscription.subscription_id
    ).node
    subscription.ckt.members[1].port.node = Node.from_subscription(
        node_b_subscription.subscription_id
    ).node

    # Here, we construct the port product block portions of the domain model:
    subscription.ckt.members[0].port.port_name = netbox_circuit.a_terminations[
        0
    ].display
    subscription.ckt.members[1].port.port_name = netbox_circuit.b_terminations[
        0
    ].display
    subscription.ckt.members[0].port.port_id = netbox_circuit.a_terminations[0].id
    port_a_description = f"Circuit Connection to {subscription.ckt.members[1].port.node.node_name} port {subscription.ckt.members[1].port.port_name}"
    subscription.ckt.members[0].port.port_description = port_a_description

    subscription.ckt.members[1].port.port_id = netbox_circuit.b_terminations[0].id
    port_b_description = f"Circuit Connection to {subscription.ckt.members[0].port.node.node_name} port {subscription.ckt.members[0].port.port_name}"
    subscription.ckt.members[1].port.port_description = port_b_description

    return {
        "subscription": subscription,
        "subscription_id": subscription.subscription_id,
    }


@step("Reserve IPs in Netbox")
def reserve_ips_in_ipam(subscription: CircuitInactive, state: State) -> State:
    """
    Reserves the IPs for this circuit in Netbox and adds them to the domain model
    """
    logger.info("Reserving IPs in NetBox")
    circuit_block_prefix = netbox.ipam.prefixes.get(CIRCUIT_PREFIX_IPAM_ID)
    # First, reserve a /64 pool for future use.
    current_circuit_prefix_64 = circuit_block_prefix.available_prefixes.create(
        {
            "prefix_length": 64,
            "description": f"{state.get('pretty_circuit')} Parent /64",
            "is_pool": "on",
        }
    )
    # Next, reserve a /127 point-to-point subnet for the circuit (from the above /64).
    current_circuit_prefix_127 = current_circuit_prefix_64.available_prefixes.create(
        {
            "prefix_length": 127,
            "description": f"{state.get('pretty_circuit')} Point-to-Point",
        }
    )
    # Now, create the NetBox IP Address entries for the devices on each side of the link:
    a_side_ip = current_circuit_prefix_127.available_ips.create(
        {
            "description": subscription.ckt.members[0].port.port_description,
            "assigned_object_type": "dcim.interface",
            "assigned_object_id": subscription.ckt.members[0].port.port_id,
            "status": "active",
        }
    )
    b_side_ip = current_circuit_prefix_127.available_ips.create(
        {
            "description": subscription.ckt.members[1].port.port_description,
            "assigned_object_type": "dcim.interface",
            "assigned_object_id": subscription.ckt.members[1].port.port_id,
            "status": "active",
        }
    )

    # Finally, add those IPv6 Addresses to the domain model.
    subscription.ckt.members[0].v6_ip_address = a_side_ip
    subscription.ckt.members[1].v6_ip_address = b_side_ip

    logger.info("Finished reserving IPs in NetBox")

    return {"subscription": subscription}


def render_circuit_endpoint_config(
    node: str,
    interface: str,
    description: str,
    address: IPv6Interface,
) -> str:
    """
    render_circuit_endpoint_config: Renders the network device config (cisco-style)
        for one side of a circuit

    Args:
        node (str): The node/router name (e.g. loc1-core).

        interface (str): The interface name (e.g. 1/1/c2/1).

        description (str): The interface description (e.g. interace-to-loc2-core:1/1/c1/1)

        address (IPv6Interface): An IPv6Interface object for adding an IP to the circuit
            interface

    Returns:
        router_config (str): The final multiline router config string that can be pasted
            into a router on one side of a circuit.
    """

    router_config = f"""! Paste the following config into {node}:
! to complete configuring the device
interface {interface}
 description {description}
 ipv6 address {address}
 ipv6 router isis
 isis network point-to-point
!
router isis
 net {ISIS_AREA_ID}
 is-type level-2-only
 metric-style wide
 passive-interface default
 no passive-interface {interface}
 address-family ipv6 unicast
  metric 10
  redistribute connected
  exit-address-family
!
end
!"""

    return router_config


@inputstep("Provide Config to User", assignee=Assignee.SYSTEM)
def provide_config_to_user(subscription: CircuitProvisioning) -> FormGenerator:
    """
    Moves the Circuit to the provisioning state and then displays the config to a
    user so that they can paste it into a router.
    """
    logger.info(f"Creating circuit payload for Circuit #{subscription.ckt.circuit_id}")
    router_a_config = render_circuit_endpoint_config(
        node=subscription.ckt.members[0].port.node.node_name,
        interface=subscription.ckt.members[0].port.port_name,
        description=subscription.ckt.members[0].port.port_description,
        address=subscription.ckt.members[0].v6_ip_address,
    )
    router_b_config = render_circuit_endpoint_config(
        node=subscription.ckt.members[1].port.node.node_name,
        interface=subscription.ckt.members[1].port.port_name,
        description=subscription.ckt.members[1].port.port_description,
        address=subscription.ckt.members[1].v6_ip_address,
    )

    class ConfigResults(FormPage):
        """FormPage for showing a user the config needed for a node"""

        a_side_router_config: LongText = ReadOnlyField(router_a_config)
        b_side_router_config: LongText = ReadOnlyField(router_b_config)
        confirm_dry_run_results: Accept = Accept("INCOMPLETE")

    logger.info("Presenting ConfigResults Form to user")
    form_data = yield ConfigResults
    user_input = form_data.dict()
    logger.info("User confirmed router config, done with ConfigResults Form")
    return user_input


@step("Update Circuit Status in Netbox")
def update_circuit_status_netbox(
    subscription: CircuitProvisioning,
) -> State:
    """
    Update the circuit state in netbox now that everything is done.
    """
    circuit = netbox.dcim.cables.get(subscription.ckt.circuit_id)
    circuit.status = "connected"
    circuit.save()

    return {"circuit_status": circuit.status}


@step("Update Subscription Description")
def update_subscription_description(
    subscription: CircuitProvisioning,
    state: State,
) -> State:
    """
    Update the subscription description to show the final circuit information.
    """
    subscription.description = f"Subscription for {state.get('pretty_circuit')}"

    return {"subscription": subscription}


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
        >> update_subscription_description
    )
