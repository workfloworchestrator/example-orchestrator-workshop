"""Workflow to initially create a circuit between two nodes."""
from typing import Any, List, Generator
from ipaddress import IPv6Interface


import structlog
from orchestrator.forms import FormPage, ReadOnlyField
from orchestrator.forms.validators import Choice, Accept, LongText
from orchestrator.targets import Target
from orchestrator.types import FormGenerator, State, SubscriptionLifecycle, UUIDstr
from orchestrator.workflow import StepList, begin, step, inputstep
from orchestrator.workflows.steps import set_status, store_process_subscription
from orchestrator.config.assignee import Assignee
from products.product_types.circuit import CircuitInactive, CircuitProvisioning
from products.product_types.node import Node
from orchestrator.services.subscriptions import (
    retrieve_subscription_by_subscription_instance_value,
)
from utils import netbox

from ..shared import CUSTOMER_UUID, create_workflow


logger = structlog.get_logger(__name__)

CIRCUIT_PREFIX_IPAM_ID = 3


def get_valid_cables_list() -> List[Any]:
    """
    Connects to netbox and returns a list of valid netbox circuits/cables.
    """
    logger.info("Connecting to Netbox to get list of available circuits/cables")
    valid_circuits = list(
        netbox.dcim.cables.filter(status="planned")
    )  # TODO: Add error handling
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

    # yield next(zip(circuit_list, pretty_circuits))
    # return zip(circuit_list, pretty_circuits) #TODO turn into a generator?


def get_next_ip() -> Any:
    pass


def initial_input_form_generator(product_name: str) -> FormGenerator:
    """
    Generates the Circuit Form to display to the user.
    """
    logger.info("Generating initial input form for Circuit")
    valid_circuits = get_valid_cables_list()
    pretty_circuits = list(format_circuits(valid_circuits))
    choices = [node[1] for node in pretty_circuits]
    CircuitEnum = Choice("CircuitEnum", zip(choices, choices))

    class CreateCircuitForm(FormPage):
        """FormPage for Creating a Circuit"""

        class Config:
            """Config class for Creating a Circuit"""

            title = product_name

        select_node_choice: CircuitEnum  # type: ignore

    user_input = yield CreateCircuitForm
    logger.info(f"User selected circuit/cable {user_input.select_node_choice}")
    circuit_data = next(
        node[0] for node in pretty_circuits if user_input.select_node_choice == node[1]
    )
    logger.info(f"circuit data is: {circuit_data.__dict__}")

    return {
        "circuit_id": circuit_data.id,
        "pretty_circuit": user_input.select_node_choice,
    }


@step("Construct Circuit model")
def construct_circuit_model(
    product: UUIDstr,
    state: State,
) -> State:
    logger.info("Building initial circuit model")

    subscription = CircuitInactive.from_product_id(
        product_id=product,
        customer_id=CUSTOMER_UUID,
        status=SubscriptionLifecycle.INITIAL,
    )

    logger.info("Adding Base Circuit Model fields to Subscription")
    subscription.ckt.circuit_id = state.get("circuit_id")
    subscription.ckt.under_maintenance = True

    logger.info("getting circuit details from netbox")
    netbox_circuit = netbox.dcim.cables.get(subscription.ckt.circuit_id)
    netbox_circuit.full_details()  # TODO: Raise error

    logger.info(
        f"Grabbing Device IDs for circuit {subscription.ckt.circuit_id} from netbox"
    )

    node_a_netbox_id = str(netbox_circuit.a_terminations[0].device.id)
    node_b_netbox_id = str(netbox_circuit.b_terminations[0].device.id)

    logger.info("Linking existing node subscriptions")
    # Get the existing node subscriptions from the DB
    # TODO: Add validator to Form Generator to make sure that these already exist.
    # TODO: Raise an error here if they don't exist
    node_a_subscription = retrieve_subscription_by_subscription_instance_value(
        resource_type="node_id", value=node_a_netbox_id
    )
    node_b_subscription = retrieve_subscription_by_subscription_instance_value(
        resource_type="node_id", value=node_b_netbox_id
    )
    # Link the existing node subscriptions from the DB to the circuit subscription
    subscription.ckt.members[0].port.node = Node.from_subscription(
        node_a_subscription.subscription_id
    ).node
    subscription.ckt.members[1].port.node = Node.from_subscription(
        node_b_subscription.subscription_id
    ).node

    subscription.ckt.members[0].port.port_name = netbox_circuit.a_terminations[
        0
    ].display
    subscription.ckt.members[1].port.port_name = netbox_circuit.b_terminations[
        0
    ].display

    # Set the port details that we have already
    subscription.ckt.members[0].port.port_id = netbox_circuit.a_terminations[0].id
    subscription.ckt.members[
        0
    ].port.port_description = f"Circuit Connection to {subscription.ckt.members[1].port.node.node_name} port {subscription.ckt.members[1].port.port_name}"

    subscription.ckt.members[1].port.port_id = netbox_circuit.b_terminations[0].id
    subscription.ckt.members[
        1
    ].port.port_description = f"Circuit Connection to {subscription.ckt.members[0].port.node.node_name} port {subscription.ckt.members[0].port.port_name}"

    return {
        "subscription": subscription,
        "subscription_id": subscription.subscription_id,
    }


@step("Reserve IPs in Netbox")
def reserve_ips_in_ipam(
    subscription: CircuitInactive,
) -> State:
    logger.info("Reserving IPs in NetBox")
    circuit_block_prefix = netbox.ipam.prefixes.get(CIRCUIT_PREFIX_IPAM_ID)
    current_circuit_prefix_64 = circuit_block_prefix.available_prefixes.create(
        {"prefix_length": 64, "description": "foo", "is_pool": "on"}
    )  # TODO: Set Description for prefix
    current_circuit_prefix_127 = current_circuit_prefix_64.available_prefixes.create(
        {"prefix_length": 127, "description": "foo", "is_pool": "on"}
    )  # TODO: Set Description for prefix
    a_side_ip = current_circuit_prefix_127.available_ips.create(
        {"description": "foo"}
    )  # TODO: Set Description for IP, add to device and interface, then set status to planning
    b_side_ip = current_circuit_prefix_127.available_ips.create(
        {"description": "foo"}
    )  # TODO: Set Description for IP, add to device and interface, then set status to planning

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
    router_config = f"""! Config for {node}
interface {interface}
 description {description}
 ipv6 address {address}
 ipv6 router isis
 isis network point-to-point
!
router isis
 net 49.0001.0123.4567.890a.0001.00
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

    form_data = yield ConfigResults
    user_input = form_data.dict()
    return user_input


@step("Update Circuit Status in Netbox")
def update_circuit_status_netbox(
    subscription: CircuitProvisioning,
) -> State:
    circuit = netbox.dcim.cables.get(subscription.ckt.circuit_id)
    circuit.status = "connected"
    circuit.save()

    return {"circuit_status": circuit.status}


@step("Update Subscription Description")
def update_subscription_description(
    subscription: CircuitProvisioning,
    state: State,
) -> State:
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
