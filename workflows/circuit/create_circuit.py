"""Workflow to initially create a circuit between two nodes."""
from typing import Any, List, Generator
import ipaddress

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

    return {"circuit_id": circuit_data.id}


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

    logger.info("Adding Node to Subscription")
    node_a_netbox_id = "7"  # TODO: Retreive this from netbox
    node_a_subscription = retrieve_subscription_by_subscription_instance_value(
        resource_type="node_id", value=node_a_netbox_id
    )

    node_b_netbox_id = "8"  # TODO: Retreive this from netbox
    node_b_subscription = retrieve_subscription_by_subscription_instance_value(
        resource_type="node_id", value=node_b_netbox_id
    )

    subscription.ckt.members[0].port.node = Node.from_subscription(
        node_a_subscription.subscription_id
    ).node
    subscription.ckt.members[1].port.node = Node.from_subscription(
        node_b_subscription.subscription_id
    ).node

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
    current_circuit_prefix_64 = circuit_block_prefix.available_prefixes.create({"prefix_length": 64, "description": "foo", "is_pool": "on"}) #TODO: Set Description for prefix
    current_circuit_prefix_127 = current_circuit_prefix_64.available_prefixes.create({"prefix_length": 127, "description": "foo", "is_pool": "on"}) #TODO: Set Description for prefix
    a_side_ip = current_circuit_prefix_127.available_ips.create({"description": "foo"}) #TODO: Set Description for IP, add to device and interface, then set status to planning
    b_side_ip = current_circuit_prefix_127.available_ips.create({"description": "foo"}) #TODO: Set Description for IP, add to device and interface, then set status to planning

    subscription.ckt.members[0].v6_ip_address = a_side_ip
    subscription.ckt.members[1].v6_ip_address = b_side_ip


    # TODO Move to new step
    subscription.ckt.members[0].port.port_id = 1
    subscription.ckt.members[0].port.port_description = "something"

    subscription.ckt.members[1].port.port_id = 1
    subscription.ckt.members[1].port.port_description = "something"
    subscription.ckt.circuit_id = 1
    subscription.ckt.under_maintenance = True

    logger.info("Finished reserving IPs in NetBox")

    return {"subscription": subscription}


@inputstep("Provide Config to User", assignee=Assignee.SYSTEM)
def provide_config_to_user(subscription: CircuitProvisioning) -> FormGenerator:
    pass


@step("Update Circuit Status in Netbox")
def update_circuit_status_netbox(
    subscription: CircuitProvisioning,
) -> State:
    pass


@step("Update Subscription Description")
def update_subscription_description(
    subscription: CircuitInactive,
) -> State:
    subscription.description = f"Circuit {subscription.ckt.circuit_id} Subscription"

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
        # >> provide_config_to_user
        # >> set_status(SubscriptionLifecycle.PROVISIONING)
        # >> update_circuit_status_netbox
        >> update_subscription_description
    )
