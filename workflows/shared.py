from typing import Callable, Optional, List

from orchestrator.db import (
    ProductTable,
    ResourceTypeTable,
    SubscriptionInstanceTable,
    SubscriptionInstanceValueTable,
    SubscriptionTable,
)
from orchestrator.targets import Target
from orchestrator.types import InputStepFunc, SubscriptionLifecycle
from orchestrator.workflow import (
    StepList,
    Workflow,
    done,
    init,
    make_workflow,
    conditional,
)
from orchestrator.workflows.steps import resync, set_status
from orchestrator.workflows.utils import wrap_create_initial_input_form


is_provisioning = conditional(
    lambda state: state["subscription"]["status"] == SubscriptionLifecycle.PROVISIONING
)
is_active = conditional(
    lambda state: state["subscription"]["status"] == SubscriptionLifecycle.ACTIVE
)

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


def retrieve_subscription_list_by_product(product_type: str, status: List[str]) -> List[SubscriptionTable]:
    """
    retrieve_subscription_list_by_product This function lets you retreive a
    list of all subscriptions of a given product type. For example, you could
    call this like so: 

    >>> retrieve_subscription_list_by_product("Node", [SubscriptionLifecycle.ACTIVE])
    [SubscriptionTable(su...note=None), SubscriptionTable(su...note=None)]

    You now have a list of all active Node subscription instances and can then
    use them in your workflow.

    Args:
        product_type (str): The prouduct type in the DB (i.e. Node, User, etc.)
        status (List[str]): The lifecycle states you want returned (i.e. 
        SubscriptionLifecycle.ACTIVE)

    Returns:
        List[SubscriptionTable]: A list of all of the subscriptions that match
        your criteria.
    """
    subscriptions = (
        SubscriptionTable.query.join(
            ProductTable,
            SubscriptionInstanceTable,
            SubscriptionInstanceValueTable,
            ResourceTypeTable,
        )
        .filter(ProductTable.product_type == product_type)
        .filter(SubscriptionTable.status.in_(status))
        .all()
    )
    return subscriptions
