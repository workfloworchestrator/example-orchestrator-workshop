"""
The home for all shared code used in the circuit workflows.
"""

from ipaddress import IPv6Interface
from typing import List

import structlog
from orchestrator.config.assignee import Assignee
from orchestrator.forms import FormPage, ReadOnlyField
from orchestrator.forms.validators import Accept, LongText
from orchestrator.types import FormGenerator
from orchestrator.workflow import inputstep
from pynetbox.models.dcim import Interfaces as PynetboxInterfaces

from products.product_types.circuit import CircuitProvisioning
from services.netbox import netbox

logger = structlog.get_logger(__name__)
# The ID of the Subnet Block we will use for assigning IPs to circuits
CIRCUIT_PREFIX_IPAM_ID = 3
ISIS_AREA_ID = "49.0001.0123.4567.890a.0001.00"


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
    valid_ports = list(netbox.dcim.interfaces.filter(device=router_name, occupied=False, speed=400000000))
    logger.debug("Found ports in Netbox", amount=len(valid_ports))
    return valid_ports


def render_circuit_endpoint_config(
    node: str,
    interface: str,
    description: str,
    address: IPv6Interface,
    isis_metric: int,
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

        isis_metric (int): The ISIS metric used for determining routing preference.

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
  metric {isis_metric}
  redistribute connected
  exit-address-family
!
end
!"""

    return router_config


def determine_isis_metric(under_maintenance: bool) -> int:
    """
    set_isis_metric determines the ISIS metric to use depending on the
    maintenance state of the circuit.

    Args:
        under_maintenance (bool): If the circuit is under the maintenance (True)
        or not (False)

    Returns:
        int: The ISIS routing metric.
    """
    if under_maintenance:
        isis_metric = 15000000
    else:
        isis_metric = 10

    return isis_metric


@inputstep("Provide Config to User", assignee=Assignee.SYSTEM)
def provide_config_to_user(subscription: CircuitProvisioning) -> FormGenerator:
    """
    Renders and displays the config to a user so that they can paste it into a router.
    """
    logger.debug(
        "Creating circuit payload for circuit",
        circuit_id=subscription.circuit.circuit_id,
    )
    isis_metric = determine_isis_metric(subscription.circuit.under_maintenance)

    router_a_config = render_circuit_endpoint_config(
        node=subscription.circuit.members[0].port.node.node_name,
        interface=subscription.circuit.members[0].port.port_name,
        description=subscription.circuit.members[0].port.port_description,
        address=subscription.circuit.members[0].v6_ip_address,
        isis_metric=isis_metric,
    )
    router_b_config = render_circuit_endpoint_config(
        node=subscription.circuit.members[1].port.node.node_name,
        interface=subscription.circuit.members[1].port.port_name,
        description=subscription.circuit.members[1].port.port_description,
        address=subscription.circuit.members[1].v6_ip_address,
        isis_metric=isis_metric,
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
