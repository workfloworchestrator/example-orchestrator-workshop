"""Workflow to initially create a circuit between two nodes."""
from typing import Dict

import structlog
from orchestrator.forms import FormPage
from orchestrator.forms.validators import Choice
from orchestrator.targets import Target
from orchestrator.types import FormGenerator, State, SubscriptionLifecycle, UUIDstr
from orchestrator.workflow import StepList, begin, step
from orchestrator.workflows.steps import set_status, store_process_subscription

from products.product_types.circuit import CircuitInactive, CircuitProvisioning
from products.product_types.node import Node
from products.services.description import description
from products.services.netbox.netbox import build_payload
from services import netbox
from workflows.circuit.shared import CIRCUIT_PREFIX_IPAM_ID, provide_config_to_user
from workflows.shared import (
    CUSTOMER_UUID,
    create_workflow,
    retrieve_subscription_list_by_product,
)

logger = structlog.get_logger(__name__)


def initial_input_form_generator(product_name: str) -> FormGenerator:
    """
    Generates the Circuit Form to display to the user.
    """
    logger.debug("Generating initial input form for Circuit")

    # First, get the data we need to present a list of circuits to a user
    node_subs = retrieve_subscription_list_by_product(
        "Node", [SubscriptionLifecycle.ACTIVE]
    )
    choices = {}
    for node in node_subs:
        choices[str(node.subscription_id)] = Node.from_subscription(
            node.subscription_id
        ).node.node_name

    # choices = {"subid": "label", "subid2": "label"}
    EndpointA = Choice("Endpoint A", zip(choices, choices.values()))

    # Next, construct the form to display to the user:
    class RouterAForm(FormPage):
        """FormPage for Creating a Circuit"""

        class Config:
            """Config class for Creating a Circuit"""

            title = product_name

        router_a: EndpointA

    # Now we present the form to the user
    logger.debug("Presenting CreateCircuitForm to user")
    router_a = yield RouterAForm

    # Now Remove previously used router from list and present new form.
    choices.pop(str(router_a.router_a.name))
    EndpointB = Choice("Endpoint B", zip(choices, choices.values()))

    class RouterBForm(FormPage):
        """FormPage for Creating a Circuit"""

        class Config:
            """Config class for Creating a Circuit"""

            title = product_name

        router_b: EndpointB

    # Now we present the form to the user
    logger.debug("Presenting CreateCircuitForm to user")
    router_b = yield RouterBForm

    # a_port_list = ["1/1/c1/1", "1/1/c2/1"]
    # b_port_list = ["2/1/c1/1", "1/1/c2/1"]

    a_port_list = {}
    for port in netbox.get_available_router_ports_by_name(
        router_name=router_a.router_a
    ):
        a_port_list[str(port.id)] = port.display
    b_port_list = {}
    for port in netbox.get_available_router_ports_by_name(
        router_name=router_b.router_b
    ):
        b_port_list[str(port.id)] = port.display

    APort = Choice(
        f"{str(router_a.router_a)} Port (Endpoint A)",
        zip(a_port_list, a_port_list.values()),
    )
    BPort = Choice(
        f"{str(router_b.router_b)} Port (Endpoint B)",
        zip(b_port_list, b_port_list.values()),
    )

    class PortSelectionForm(FormPage):
        """FormPage for Creating a Circuit"""

        class Config:
            """Config class for Creating a Circuit"""

            title = "Choose circuit ports"

        a_port: APort
        b_port: BPort

    ports = yield PortSelectionForm

    # Once we get the form selecton back from the user we send that circuit ID
    # to the state object for use in generating the subscription
    logger.debug(
        "User selected a circuit/cable",
    )

    logger.debug("Done with CreateCircuitForm")

    return {
        "router_a": router_a.router_a.name,
        "router_b": router_b.router_b.name,
        "ports": ports,
    }


@step("Construct Circuit model")
def construct_circuit_model(
    product: UUIDstr,
    ports: Dict[str, str],
    router_a: Node,
    router_b: Node,
) -> State:
    """
    Construct the initial domain model for circuit
    """
    logger.debug("Building initial circuit model")

    # First, we instantiate an empty subscription for a circuit subscription:
    subscription = CircuitInactive.from_product_id(
        product_id=product,
        customer_id=CUSTOMER_UUID,
        status=SubscriptionLifecycle.INITIAL,
    )

    # Next, we add the circuit details to the subscription
    logger.debug("Adding Base Circuit Model fields to Subscription")

    a_port = netbox.get_interface_by_device_and_name(
        device=router_a.node.node_name, name=ports["a_port"]
    )
    b_port = netbox.get_interface_by_device_and_name(
        device=router_b.node.node_name, name=ports["b_port"]
    )

    # Add A-side and B-side to the circuit subscription:
    subscription.circuit.members[0].port.node = router_a.node
    subscription.circuit.members[0].port.port_id = a_port.id
    subscription.circuit.members[0].port.port_name = a_port.display
    subscription.circuit.members[1].port.node = router_b.node
    subscription.circuit.members[1].port.port_id = b_port.id
    subscription.circuit.members[1].port.port_name = b_port.display

    # Generate the port descriptions to be used in the config shown to the user
    subscription.circuit.members[0].port.port_description = description(
        subscription.circuit.members[0]
    )
    subscription.circuit.members[1].port.port_description = description(
        subscription.circuit.members[1]
    )

    # Set generic circuit subscription fields
    subscription.circuit.circuit_status = "planned"
    subscription.circuit.under_maintenance = True
    subscription.circuit.circuit_description = description(subscription.circuit)

    return {
        "subscription": subscription,
        "subscription_id": subscription.subscription_id,
    }


@step("Reserve IPs in Netbox")
def reserve_ips_in_ipam(subscription: CircuitInactive) -> State:
    """
    Reserves the IPs for this circuit in Netbox and adds them to the domain model
    """
    logger.debug("Reserving IPs in NetBox")
    # # First, reserve a /64 pool for future use.
    current_circuit_prefix_64 = netbox.create_available_prefix(
        parent_id=CIRCUIT_PREFIX_IPAM_ID,
        payload=netbox.AvailablePrefixPayload(
            prefix_length=64,
            description=f"{subscription.circuit.circuit_description} Parent /64",
            is_pool=True,
        ),
    )

    # Next, reserve a /127 point-to-point subnet for the circuit (from the above /64).
    current_circuit_prefix_127 = netbox.create_available_prefix(  # TODO
        parent_id=current_circuit_prefix_64.id,
        payload=netbox.AvailablePrefixPayload(
            prefix_length=127,
            description=f"{subscription.circuit.circuit_description} Point-to-Point",
        ),
    )
    # Now, create the NetBox IP Address entries for the devices on each side of the link:
    a_side_ip = netbox.create_available_ip(
        parent_id=current_circuit_prefix_127.id,
        payload=netbox.AvailableIpPayload(
            description=subscription.circuit.members[0].port.port_description,
            assigned_object_id=subscription.circuit.members[0].port.port_id,
        ),
    )
    b_side_ip = netbox.create_available_ip(
        parent_id=current_circuit_prefix_127.id,
        payload=netbox.AvailableIpPayload(
            description=subscription.circuit.members[1].port.port_description,
            assigned_object_id=subscription.circuit.members[1].port.port_id,
        ),
    )

    # Finally, add those IPv6 Addresses to the domain model.
    subscription.circuit.members[0].v6_ip_address = a_side_ip
    subscription.circuit.members[1].v6_ip_address = b_side_ip

    logger.debug(
        "Finished reserving IPs in NetBox",
        a_side_ip=subscription.circuit.members[0].v6_ip_address,
        b_side_ip=subscription.circuit.members[1].v6_ip_address,
    )

    return {"subscription": subscription}


@step("Update subscription description")
def update_circuit_description(subscription: CircuitProvisioning) -> State:
    """Updates the circuit description."""
    subscription.description = description(subscription)
    return {"subscription": subscription}


@step("Set Circuit in service")
def set_circuit_in_service(subscription: CircuitProvisioning) -> State:
    """Set the circuit status to connected."""
    subscription.circuit.circuit_status = "connected"
    return {"subscription": subscription}


@step("Create Circuit in Netbox")
def create_circuit_in_netbox(subscription: CircuitProvisioning) -> State:
    """Creates a circuit in Netbox"""
    netbox_payload = build_payload(subscription.circuit, subscription)
    subscription.circuit.circuit_id = netbox.create(netbox_payload)
    return {"subscription": subscription, "netbox_payload": netbox_payload.dict()}


@step("Update Circuit in Netbox")
def update_circuit_in_netbox(subscription: CircuitProvisioning) -> State:
    """Updates a circuit in Netbox"""
    netbox_payload = build_payload(subscription.circuit, subscription)
    return {
        "netbox_payload": netbox_payload.dict(),
        "netbox_updated": netbox.update(netbox_payload),
    }


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
        >> set_status(SubscriptionLifecycle.PROVISIONING)
        >> create_circuit_in_netbox
        >> update_circuit_description
        >> update_circuit_in_netbox
        >> provide_config_to_user
        >> set_circuit_in_service
        >> update_circuit_in_netbox
    )
