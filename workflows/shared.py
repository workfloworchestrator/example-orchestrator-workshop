from typing import Callable, Optional

from orchestrator.targets import Target
from orchestrator.types import InputStepFunc, State, SubscriptionLifecycle, UUIDstr
from orchestrator.workflow import StepList, Workflow, done, init, make_workflow, conditional, step
from orchestrator.workflows.steps import resync, set_status
from orchestrator.workflows.utils import wrap_create_initial_input_form

from products.product_types.node import Node
from utils import netbox

is_provisioning = conditional(lambda state: state["subscription"]["status"] == SubscriptionLifecycle.PROVISIONING)
is_active = conditional(lambda state: state["subscription"]["status"] == SubscriptionLifecycle.ACTIVE)

CUSTOMER_UUID = "b727dd2c-55f3-4d19-8452-a32f15b00123"


def create_workflow(
    description: str,
    initial_input_form: Optional[InputStepFunc] = None,
    status: SubscriptionLifecycle = SubscriptionLifecycle.ACTIVE,
) -> Callable[[Callable[[], StepList]], Workflow]:
    """Transform an initial_input_form and a step list into a workflow with a target=Target.CREATE.

    Use this for create workflows only.

    Example::

        @create_workflow("create service port")
        def create_service_port() -> StepList:
            do_something
            >> do_something_else
    """
    create_initial_input_form_generator = wrap_create_initial_input_form(
        initial_input_form
    )

    def _create_workflow(f: Callable[[], StepList]) -> Workflow:
        steplist = init >> f() >> set_status(status) >> resync >> done
        return make_workflow(
            f, description, create_initial_input_form_generator, Target.CREATE, steplist
        )

    return _create_workflow


@step("Load relevant Node subscription information")
def load_node_subscription_info(subscription_id: UUIDstr) -> State:
    subscription = Node.from_subscription(subscription_id)
    nodes = netbox.dcim.get_devices()
    node = next(node for node in nodes if node.get("name") == subscription.node.node_name)
    return {
        "subscription": subscription,
        "node": node,
    }