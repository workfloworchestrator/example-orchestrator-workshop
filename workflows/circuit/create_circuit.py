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
from utils import netbox

from ..shared import CUSTOMER_UUID, create_workflow


logger = structlog.get_logger(__name__)


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
    pretty_circuits = format_circuits(valid_circuits)
    choices = [node[1] for node in pretty_circuits]
    CircuitEnum = Choice("CircuitEnum", zip(choices, choices))

    class CreateCircuitForm(FormPage):
        """FormPage for Creating a Circuit"""

        class Config:
            """Config class for Creating a Circuit"""

            title = product_name

        select_node_choice: CircuitEnum  # type: ignore

    user_input = yield CreateCircuitForm
    circuit_data = next(
        node for node in pretty_circuits if user_input.select_node_choice == node[1]
    )

    return {"circuit_id": circuit_data[0].id}


@step("Construct Node model")
def construct_circuit_model(
    product: UUIDstr,
    node_id: int,
    node_name: str,
) -> State:
    pass


@step("Reserve IPs in Netbox")
def reserve_ips_in_ipam(
    subscription: CircuitInactive,
) -> State:
    pass


@inputstep("Provide Config to User", assignee=Assignee.SYSTEM)
def provide_config_to_user(subscription: CircuitProvisioning) -> FormGenerator:
    pass


@step("Update Circuit Status in Netbox")
def update_circuit_status_netbox(
    subscription: CircuitProvisioning,
) -> State:
    pass


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
    )
