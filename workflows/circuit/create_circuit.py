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
from utils import netbox
from workflows.circuit.shared import (
    CIRCUIT_PREFIX_IPAM_ID,
    fetch_available_router_ports_by_name,
    generate_circuit_description,
    generate_interface_description,
    provide_config_to_user,
)
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
    choices.pop(str(router_a.router_a._name_))
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
    for port in fetch_available_router_ports_by_name(router_name=router_a.router_a):
        a_port_list[str(port.id)] = port.display
    b_port_list = {}
    for port in fetch_available_router_ports_by_name(router_name=router_b.router_b):
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
        "router_a": router_a.router_a._name_,
        "router_b": router_b.router_b._name_,
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

    a_port = list(
        netbox.dcim.interfaces.filter(
            device=router_a.node.node_name, name=ports["a_port"]
        )
    )[0]
    b_port = list(
        netbox.dcim.interfaces.filter(
            device=router_b.node.node_name, name=ports["b_port"]
        )
    )[0]
    netbox_circuit = netbox.dcim.cables.create(
        a_terminations=[{"object_id": a_port.id, "object_type": "dcim.interface"}],
        b_terminations=[{"object_id": b_port.id, "object_type": "dcim.interface"}],
        status="planned",
    )

    subscription.circuit.circuit_id = netbox_circuit.id
    subscription.circuit.under_maintenance = True

    # Link the existing node subscriptions from the DB to the circuit subscription:
    subscription.circuit.members[0].port.node = router_a.node
    subscription.circuit.members[1].port.node = router_b.node

    # Here, we construct the port product block portions of the domain model:
    subscription.circuit.members[0].port.port_name = netbox_circuit.a_terminations[
        0
    ].display
    subscription.circuit.members[1].port.port_name = netbox_circuit.b_terminations[
        0
    ].display
    subscription.circuit.members[0].port.port_id = netbox_circuit.a_terminations[0].id
    port_a_description = generate_interface_description(
        remote_device=subscription.circuit.members[1].port.node.node_name,
        remote_port=subscription.circuit.members[1].port.port_name,
    )
    subscription.circuit.members[0].port.port_description = port_a_description

    subscription.circuit.members[1].port.port_id = netbox_circuit.b_terminations[0].id
    port_b_description = generate_interface_description(
        remote_device=subscription.circuit.members[0].port.node.node_name,
        remote_port=subscription.circuit.members[0].port.port_name,
    )
    subscription.circuit.members[1].port.port_description = port_b_description

    # Generate the circuit description to be used by various later things
    circuit_description = generate_circuit_description(
        circuit_id=subscription.circuit.circuit_id,
        a_side_device=subscription.circuit.members[0].port.node.node_name,
        a_side_port=subscription.circuit.members[0].port.port_name,
        b_side_device=subscription.circuit.members[1].port.node.node_name,
        b_side_port=subscription.circuit.members[1].port.port_name,
    )

    subscription.circuit.circuit_description = circuit_description

    # Update netbox's planned circuit with the circuit description
    netbox_circuit.description = circuit_description
    netbox_circuit.save()

    return {
        "subscription": subscription,
        "subscription_id": subscription.subscription_id,
    }


@step("Reserve IPs in Netbox")
def reserve_ips_in_ipam(
    subscription: CircuitInactive,
) -> State:
    """
    Reserves the IPs for this circuit in Netbox and adds them to the domain model
    """
    logger.debug("Reserving IPs in NetBox")
    circuit_block_prefix = netbox.ipam.prefixes.get(CIRCUIT_PREFIX_IPAM_ID)
    # First, reserve a /64 pool for future use.
    current_circuit_prefix_64 = circuit_block_prefix.available_prefixes.create(
        {
            "prefix_length": 64,
            "description": f"{subscription.circuit.circuit_description} Parent /64",
            "is_pool": "on",
        }
    )
    # Next, reserve a /127 point-to-point subnet for the circuit (from the above /64).
    current_circuit_prefix_127 = current_circuit_prefix_64.available_prefixes.create(
        {
            "prefix_length": 127,
            "description": f"{subscription.circuit.circuit_description} Point-to-Point",
        }
    )
    # Now, create the NetBox IP Address entries for the devices on each side of the link:
    a_side_ip = current_circuit_prefix_127.available_ips.create(
        {
            "description": subscription.circuit.members[0].port.port_description,
            "assigned_object_type": "dcim.interface",
            "assigned_object_id": subscription.circuit.members[0].port.port_id,
            "status": "active",
        }
    )
    b_side_ip = current_circuit_prefix_127.available_ips.create(
        {
            "description": subscription.circuit.members[1].port.port_description,
            "assigned_object_type": "dcim.interface",
            "assigned_object_id": subscription.circuit.members[1].port.port_id,
            "status": "active",
        }
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


@step("Update Circuit Status in Netbox")
def update_circuit_status_netbox(
    subscription: CircuitProvisioning,
) -> State:
    """
    Update the circuit state in netbox now that everything is done.
    """
    circuit = netbox.dcim.cables.get(subscription.circuit.circuit_id)
    circuit.status = "connected"
    circuit.save()

    return {"circuit_status": circuit.status}


@step("Update Subscription Description")
def update_subscription_description(
    subscription: CircuitProvisioning,
) -> State:
    """
    Update the subscription description to show the final circuit information.
    """

    subscription.description = (
        f"Subscription for {subscription.circuit.circuit_description}"
    )

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
