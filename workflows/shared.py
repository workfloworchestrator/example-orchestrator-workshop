from inspect import isgeneratorfunction
from typing import Callable, List, Optional, cast

from orchestrator.db import (
    ProductTable,
    ResourceTypeTable,
    SubscriptionInstanceTable,
    SubscriptionInstanceValueTable,
    SubscriptionTable,
)
from orchestrator.targets import Target
from orchestrator.types import FormGenerator, InputForm, InputStepFunc, State, StateInputStepFunc, SubscriptionLifecycle
from orchestrator.utils.state import form_inject_args
from orchestrator.workflow import StepList, Workflow, conditional, done, init, make_workflow
from orchestrator.workflows.steps import resync, set_status, store_process_subscription, unsync
from orchestrator.workflows.utils import _generate_modify_form, wrap_create_initial_input_form

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
    create_initial_input_form_generator = wrap_create_initial_input_form(initial_input_form)

    def _create_workflow(f: Callable[[], StepList]) -> Workflow:
        steplist = init >> f() >> set_status(status) >> resync >> done
        return make_workflow(f, description, create_initial_input_form_generator, Target.CREATE, steplist)

    return _create_workflow


def wrap_modify_initial_input_form(initial_input_form: Optional[InputStepFunc]) -> Optional[StateInputStepFunc]:
    """Wrap initial input for modify and terminate workflows.

    This is needed because the frontend expects all modify workflows to start with a page that only contains the
    subscription id. It also expects the second page to have some user visible inputs and the subscription id *again*.
    """

    def create_initial_input_form_generator(state: State) -> FormGenerator:
        workflow_target: str = state["workflow_target"]
        workflow_name: str = state["workflow_name"]

        user_input = yield _generate_modify_form(workflow_target, workflow_name)

        subscription = SubscriptionTable.query.get(user_input.subscription_id)

        begin_state = {
            "subscription_id": str(subscription.subscription_id),
            "product": str(subscription.product_id),
            "organisation": str(subscription.customer_id),
        }

        if initial_input_form is None:
            return begin_state

        form = form_inject_args(initial_input_form)({**state, **begin_state})

        if isgeneratorfunction(initial_input_form):
            user_input = yield from cast(FormGenerator, form)
        else:
            user_input_model = yield cast(InputForm, form)
            user_input = user_input_model.dict()

        return {**begin_state, **user_input}

    return create_initial_input_form_generator


def modify_workflow(
    description: str, initial_input_form: Optional[InputStepFunc] = None
) -> Callable[[Callable[[], StepList]], Workflow]:
    """Transform an initial_input_form and a step list into a workflow.

    Use this for modify workflows.

    Example::

        @modify_workflow("create service port") -> StepList:
        def create_service_port():
            do_something
            >> do_something_else
    """

    wrapped_modify_initial_input_form_generator = wrap_modify_initial_input_form(initial_input_form)

    def _modify_workflow(f: Callable[[], StepList]) -> Workflow:
        steplist = (
            init
            >> store_process_subscription(Target.MODIFY)
            >> unsync
            >> f()
            >> resync
            >> done
        )  # fmt: skip

        return make_workflow(f, description, wrapped_modify_initial_input_form_generator, Target.MODIFY, steplist)

    return _modify_workflow


def terminate_workflow(
    description: str, initial_input_form: Optional[InputStepFunc] = None
) -> Callable[[Callable[[], StepList]], Workflow]:
    """Transform an initial_input_form and a step list into a workflow.

    Use this for terminate workflows.

    Example::

        @terminate_workflow("create service port") -> StepList:
        def create_service_port():
            do_something
            >> do_something_else
    """

    wrapped_terminate_initial_input_form_generator = wrap_modify_initial_input_form(initial_input_form)

    def _terminate_workflow(f: Callable[[], StepList]) -> Workflow:
        steplist = (
            init
            >> store_process_subscription(Target.TERMINATE)
            >> unsync
            >> f()
            >> set_status(SubscriptionLifecycle.TERMINATED)
            >> resync
            >> done
        )

        return make_workflow(f, description, wrapped_terminate_initial_input_form_generator, Target.TERMINATE, steplist)

    return _terminate_workflow


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
        List[SubscriptionTable]: A list of all the subscriptions that match
        your criteria.
    """
    subscriptions = (
        SubscriptionTable.query.join(ProductTable)
        .filter(ProductTable.product_type == product_type)
        .filter(SubscriptionTable.status.in_(status))
        .all()
    )
    return subscriptions
