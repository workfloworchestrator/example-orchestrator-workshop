from typing import List
from ipaddress import IPv6Interface

import structlog
from pynetbox.models.dcim import Interfaces as PynetboxInterfaces

from utils import netbox


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


def fetch_available_router_ports_by_name(router_name: str) -> List[PynetboxInterfaces]:
    """
    fetch_available_router_ports_by_name fetches a list of available ports from netbox
        when given the name of a router. To be considered available, the port must be:
            1) A 400G interface (any media type)
            2) On the router specified.
            3) Not "occupied" from netbox's perspective.

    Args:
        router_name (str): the router that you need to find an open port from, i.e. "loc1-core".

    Returns:
        List[PynetboxInterfaces]: a list of valid interfaces from netbox.
    """
    valid_ports = list(
        netbox.dcim.interfaces.filter(
            device=router_name, occupied=False, speed=400000000
        )
    )
    logger.debug("Found ports in Netbox", amount=len(valid_ports))
    return valid_ports


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

