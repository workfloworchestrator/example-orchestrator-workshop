"""Workflow to initially create a circuit between two nodes."""
from ipaddress import IPv6Interface
from typing import Any, Dict, List

import structlog
from orchestrator.config.assignee import Assignee
from orchestrator.forms import FormPage, ReadOnlyField
from orchestrator.forms.validators import Accept, Choice, LongText
from orchestrator.targets import Target
from orchestrator.types import FormGenerator, State, SubscriptionLifecycle, UUIDstr
from orchestrator.workflow import StepList, begin, inputstep, step
from orchestrator.workflows.steps import set_status, store_process_subscription

from products.product_types.circuit import CircuitInactive, CircuitProvisioning
from products.product_types.node import Node
from utils import netbox
from workflows.shared import (
    CUSTOMER_UUID,
    create_workflow,
    retrieve_subscription_list_by_product,
)

logger = structlog.get_logger(__name__)

# The ID of the Subnet Block we will use for assigning IPs to circuits
CIRCUIT_PREFIX_IPAM_ID = 3
ISIS_AREA_ID = "49.0001.0123.4567.890a.0001.00"


def generate_circuit_description(
    circuit_id: int,
    a_side_device: str,
    a_side_port: str,
    b_side_device: str,
    b_side_port: str,
) -> str:
    """
    generate_circuit_description creates a circuit description that is used by The Orchestrator
    and any system that needs to generate a circuit description. This function holds the
    business logic for doing so.

    Args:
        circuit_id (int): This is the circuit ID that is in netbox. This is a unique
            integer to this circuit. (i.e. 7)

        a_side_device (str): This is the name of the device on the "A" side of the circuit. For
            netbox's API, this is the first item in the list of circuit endpoints. (i.e. loc1-core)

        a_side_port (str): This is the name of the port on the "A" side of the circuit. For
            netbox's API, this is the first item in the list of circuit endpoints. (i.e. 1/1/c2/1)

        b_side_device (str): This is the name of the device on the "B" side of the circuit. For
            netbox's API, this is the second item in the list of circuit endpoints. (i.e. loc2-core)

        b_side_port (str): This is the name of the port on the "B" side of the circuit. For
            netbox's API, this is the first item in the list of circuit endpoints. (i.e. 1/1/c1/1)

    Returns:
        str: The assembled circuit description. Given the examples above this function would return:
        "Circuit ID 7: loc1-core:1/1/c2/1 <--> loc2-core:1/1/c1/1"
    """
    return f"Circuit ID {circuit_id}: {a_side_device}:{a_side_port} <--> {b_side_device}:{b_side_port}"


def generate_interface_description(
    remote_device: str,
    remote_port: str,
) -> str:
    """
    generate_interface_description creates an interface description that is used by The Orch
    and any system that needs to generate an interface description. This function holds the
    business logic for doing so.

    Args:
        remote_device (str): This is the name of the device on the far side of the circuit
            from this interface's perspective. (i.e. loc2-core)
        remote_port (str): This is the name of the port on the far side of the circuit
            from this interface's perspective. (i.e. 1/1/c1/1)

    Returns:
        str: The assembled interface description. Given the examples above this function would return:
        "Circuit Connection to loc2-core port 1/1/c1/1"
    """
    return f"Circuit Connection to {remote_device} port {remote_port}"


def fetch_available_router_ports_by_name(router_name: str) -> List[Any]:
    valid_ports = list(
        netbox.dcim.interfaces.filter(
            device=router_name, occupied=False, speed=400000000
        )
    )
    logger.debug("Found ports in Netbox", amount=len(valid_ports))
    return valid_ports


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
    Renders and displays the config to a user so that they can paste it into a router.
    """
    logger.debug(
        "Creating circuit payload for circuit",
        circuit_id=subscription.circuit.circuit_id,
    )
    router_a_config = render_circuit_endpoint_config(
        node=subscription.circuit.members[0].port.node.node_name,
        interface=subscription.circuit.members[0].port.port_name,
        description=subscription.circuit.members[0].port.port_description,
        address=subscription.circuit.members[0].v6_ip_address,
    )
    router_b_config = render_circuit_endpoint_config(
        node=subscription.circuit.members[1].port.node.node_name,
        interface=subscription.circuit.members[1].port.port_name,
        description=subscription.circuit.members[1].port.port_description,
        address=subscription.circuit.members[1].v6_ip_address,
    )

    class ConfigResults(FormPage):
        """FormPage for showing a user the config needed for a node"""

        endpoint_a_router_config: LongText = ReadOnlyField(router_a_config)
        endpoint_b_router_config: LongText = ReadOnlyField(router_b_config)
        confirm_config_put_on_routers: Accept = Accept("INCOMPLETE")

    logger.debug("Presenting ConfigResults Form to user")
    form_data = yield ConfigResults
    user_input = form_data.dict()
    logger.debug("User confirmed router config, done with ConfigResults Form")
    return user_input


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
